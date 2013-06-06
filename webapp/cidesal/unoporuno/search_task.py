#/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Copyright (c) 2010-2012 Jorge J. García Flores, LIMSI/CNRS

## This file is part of Unoporuno.

##     Unoporuno is free software: you can redistribute it and/or modify
##     it under the terms of the GNU General Public License as published by
##     the Free Software Foundation, either version 3 of the License, or
##     (at your option) any later version.

##     Unoporuno is distributed in the hope that it will be useful,
##     but WITHOUT ANY WARRANTY; without even the implied warranty of
##     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##     GNU General Public License for more details.

##     You should have received a copy of the GNU General Public License
##     along with Unoporuno.  If not, see <http://www.gnu.org/licenses/>.
##
# usage: python db_converging_pipelines.py input_file.csv output_folder [research_name] [True|False|All] ['users'] ['description']
#
# [1] input_file.csv = input csv file with people|topics|organizations|geography
# [2] output_folder = ./outputfolder
# [3] research_name = id or name for this batch research; name creates a new search, id updates an existing search
# [4] [True|False|All] = FG filter selection
# [5] users
# [6] description
# Programmed by Jorge García Flores on 1st june 2011
# LIMSI/CNRS
# *****
# TODO: cuando el archivo de entrada venga con link, actualizar unoporuno_snippet.evidence_type
# TODO: en búsquedas como la de los argentinos, cuanto tiene un link de evidencia detiene la búsqueda
SNIPPET_DESCRIPTION_LENGTH = 500
SNIPPET_LINK_LENGTH = 400
COLUMN_SEPARATOR = '|'
ROW_SIZE=6
TOPIC_SEPARATOR = ';'


import sys, datetime, os, re, logging
import time, logging, copy, ConfigParser

from lxml import etree


class UnoporunoSearch(object):
    def __init__(self, nombre, archivo, usuario, descripcion='', file_type='xls'):
        self.arg_input_file = archivo
        self.arg_output_folder = archivo +'.'+ usuario
        self.arg_research_name = nombre
        self.arg_FG_sel = 'True'
        self.arg_users = usuario
        self.arg_description = descripcion
        self.file_type = file_type

        
        logging.basicConfig(level=logging.INFO)
        config = ConfigParser.ConfigParser()
        try:
            config.read("unoporuno.conf")
        except:
            logging.error("No configuration file on unoporuno.conf")
            exit(-1)
        if len(config.sections())==0:
            config.read(os.environ['HOME']+"/.unoporuno/unoporuno.conf")
            if len(config.sections())==0:
                logging.error("No configuration file on unoporuno.conf")
                exit(-1)
        UNOPORUNO_ROOT = config.get('unoporuno', 'root')
        UNOPORUNO_PATH = UNOPORUNO_ROOT + '/module/'
        CIDESAL_WEBAPP_PATH= UNOPORUNO_ROOT + '/webapp/'

        if not UNOPORUNO_PATH in sys.path:
            sys.path.append(UNOPORUNO_PATH)
        from dospordos.buscador import BuscadorDiasporas, ErrorBuscador
        from dospordos.features import RegexFeature, FeatureError, GazetteerFeature, QualifiedGazetteerFeature
        from dospordos.tools import DiasporaOutput, PersonasInput, FileFormatError
        from busqueda_db.busqueda_db import Busqueda_DB


        if not CIDESAL_WEBAPP_PATH in sys.path:
            sys.path.append(CIDESAL_WEBAPP_PATH)
            sys.path.append(CIDESAL_WEBAPP_PATH+'cidesal/')
        from unoporuno.models import Busqueda, Persona, Snippet, Vinculo

        buscador = BuscadorDiasporas()

        personas_file = PersonasInput()
        if self.file_type=='csv':
            personas_file.open_csv(self.arg_input_file)
        elif self.file_type=='xls':
            personas_file.open_xls(self.arg_input_file)
        else:
            raise FileFormatError, "Unrecognized file format: %s" % (self.file_type)
        output_folder = self.arg_output_folder
        personas = personas_file.read()
        personas_procesadas = 0
        

        nombre_busqueda = self.arg_research_name
        filter_value = self.arg_FG_sel
        logging.debug(' filter_value' +filter_value)
        user = self.arg_users
        description = self.arg_description

        nueva_busqueda = Busqueda()
        nueva_busqueda.nombre = nombre_busqueda
        nueva_busqueda.fecha = datetime.datetime.now()
        nueva_busqueda.usuario = user
        nueva_busqueda.descripcion = description
        nueva_busqueda.status = '@' +str(personas_procesadas) +'/'+ str(len(personas))
        nueva_busqueda.save()
        nombre_busqueda = str(nueva_busqueda.id)
       
        db_busqueda = Busqueda_DB(UNOPORUNO_ROOT)

        OrganizationRegex = RegexFeature(UNOPORUNO_ROOT, 'organization')
        CountryGazet = QualifiedGazetteerFeature(UNOPORUNO_ROOT, 'country',False)
        CountryGazetCase = QualifiedGazetteerFeature(UNOPORUNO_ROOT, 'country',True)
        CityGazet = QualifiedGazetteerFeature(UNOPORUNO_ROOT, 'city', False)
        CityGazetCase = QualifiedGazetteerFeature(UNOPORUNO_ROOT, 'city', True)
        AccronymGazet = GazetteerFeature(UNOPORUNO_ROOT, 'accronym', True)
        BiophrasesRegex = RegexFeature(UNOPORUNO_ROOT, 'biographical phrases')
        ProfessionRegex = RegexFeature(UNOPORUNO_ROOT, 'profession')
        ProfessionGazt = GazetteerFeature(UNOPORUNO_ROOT, 'profession')
        DegreeRegex = RegexFeature(UNOPORUNO_ROOT, 'degree')
        DegreeGazt = GazetteerFeature(UNOPORUNO_ROOT, 'degree')
        CvRegex = RegexFeature(UNOPORUNO_ROOT, 'cv general')
        CvHttpRegex = RegexFeature(UNOPORUNO_ROOT, 'cv http')
        LatinNatRegex = RegexFeature(UNOPORUNO_ROOT, 'latin nationalities')
        WorldNatRegex = RegexFeature(UNOPORUNO_ROOT, 'world nationalities es')
        WorldNatGazt = GazetteerFeature(UNOPORUNO_ROOT, 'world nationalities en')
        EmailRegex = RegexFeature(UNOPORUNO_ROOT, 'email')
        PublicationRegex = RegexFeature(UNOPORUNO_ROOT, 'publication')
        PublicationHttpRegex = RegexFeature(UNOPORUNO_ROOT, 'publication http')
        linked_re = re.compile('linkedin\.com/')
        TesisRegex = RegexFeature(UNOPORUNO_ROOT, 'thesis')
        TesisHttpRegex = RegexFeature(UNOPORUNO_ROOT, 'thesis http')
        BlacklistHttpRegex = RegexFeature(UNOPORUNO_ROOT, 'blacklist http')

#*******************************************************
#                    BÚSQUEDA GOOGLE
#*******************************************************


        
        for p in personas:
            if not p.nombre:
                continue
            logging.info ('batch_diaspora_search::processing '+ p.nombre)
            #********
            # PIPELINE name
            #********
            name_output_folder = output_folder+'/results_name'
            diaspora_output = DiasporaOutput(name_output_folder)
            diaspora_output.open_person(p)
            r = reloj()
            buscador.inicia(p.nombre, p.vinculo)
            r.start()
            resultado_name = buscador.genera_busquedas_nominales()  
            name_list = resultado_name.filtra_nominal(p.nombre)        
            r.stop()
            logging.debug('converging::name_list.snippets = ' +str(len(name_list)))        


            ps = PipelineStats()
            ps.type = 'name'
            ps.total_queries = resultado_name.total_queries
            ps.total_snippets = len(resultado_name.snippets)
            ps.tiempo_proceso = r.tiempo()[0]
            ps.encontro_vinculo = resultado_name.vinculo_encontrado        
            diaspora_output.write_pipeline(ps, list(resultado_name.snippets))
            if ps.encontro_vinculo:
                diaspora_output.close_person()
                continue
            diaspora_output.close_person()

            #********
            # PIPELINE geo
            #********
            geo_list = []
            if len(p.lugares)>0:
                geo_output_folder = output_folder+'/results_geo'
                diaspora_output = DiasporaOutput(geo_output_folder)
                diaspora_output.open_person(p)

                r.start()
                resultado_geo = buscador.genera_busquedas_geograficas(p.lugares)
                geo_list=resultado_geo.filtra_nominal(p.nombre)
                r.stop()
                logging.debug('converging::resultado_geo.snippets = ' +str(len(geo_list)))
                ps = PipelineStats()
                ps.type = 'geo'
                ps.total_queries = resultado_geo.total_queries
                ps.total_snippets = len(resultado_geo.snippets)
                ps.tiempo_proceso = r.tiempo()[0]
                ps.encontro_vinculo = resultado_geo.vinculo_encontrado
                diaspora_output.write_pipeline(ps, list(resultado_geo.snippets))
                if ps.encontro_vinculo:
                    diaspora_output.close_person()
                    continue
                diaspora_output.close_person()

            #********
            # PIPELINE topics 
            #********
            topics_list = []
            if len(p.temas)>0:
                topics_output_folder = output_folder+'/results_topics'
                diaspora_output = DiasporaOutput(topics_output_folder)
                diaspora_output.open_person(p)
                r.start()
                resultado_topics = buscador.genera_busquedas_tematicas(p.temas)
                topics_list = resultado_topics.filtra_nominal(p.nombre)
                r.stop()
                logging.debug('converging::topics_list = ' +str(len(topics_list)))        
                ps = PipelineStats()
                ps.type = 'topics'
                ps.total_queries = resultado_topics.total_queries
                ps.total_snippets = len(resultado_topics.snippets)
                ps.tiempo_proceso = r.tiempo()[0]
                ps.encontro_vinculo = resultado_topics.vinculo_encontrado
                diaspora_output.write_pipeline(ps, list(resultado_topics.snippets))
                if ps.encontro_vinculo:
                    diaspora_output.close_person()
                    continue
                diaspora_output.close_person()

            #********
            # PIPELINE orgs
            #********
            orgs_list = []
            if len(p.orgs)>0:
                orgs_output_folder = output_folder+'/results_orgs'
                diaspora_output = DiasporaOutput(orgs_output_folder)
                diaspora_output.open_person(p)

                r.start()
                resultado_orgs = buscador.genera_busquedas_organizacionales(p.orgs)
                orgs_list = resultado_orgs.filtra_nominal(p.nombre)
                r.stop()
                logging.debug('converging::resultado_orgs.snippets = ' +str(len(orgs_list)))
                ps = PipelineStats()
                ps.type = 'orgs'
                ps.total_queries = resultado_orgs.total_queries
                ps.total_snippets = len(resultado_orgs.snippets)
                ps.tiempo_proceso = r.tiempo()[0]
                ps.encontro_vinculo = resultado_orgs.vinculo_encontrado
                diaspora_output.write_pipeline(ps, list(resultado_orgs.snippets))
                if ps.encontro_vinculo:
                    diaspora_output.close_person()
                    continue
                diaspora_output.close_person()

            # ********
            # NEW PIPELINE convergent
            # ********
            conv_output_folder = output_folder+'/results_converging'
            diaspora_output = DiasporaOutput(conv_output_folder)
            diaspora_output.open_person(p)

            r.start()
            name_links = set([])
            geo_links = set([])
            orgs_links = set([])
            topics_links = set([])

            unique_snippets_list = name_list + geo_list + orgs_list + topics_list
            logging.debug('converging::len(name_snippets_set)= ' +str(len(name_list)))
            logging.debug('converging::len(geo_snippets_set)= ' +str(len(geo_list)))
            logging.debug('converging::len(topics_snippets_set)= ' +str(len(topics_list)))
            logging.debug('converging::len(orgs_snippets_set)= ' +str(len(orgs_list)))
            logging.debug('converging::len(unique_snippets_set)= ' +str(len(unique_snippets_list)))

            for s in name_list:
                name_links.add(s.link)
            for s in geo_list:
                geo_links.add(s.link)
            for s in orgs_list:
                orgs_links.add(s.link)
            for s in topics_list:
                topics_links.add(s.link)    

            convergent_4 = []
            convergent_3 = []
            convergent_2 = []
            convergent_1 = []

            for s in unique_snippets_list:
                logging.debug('for s in unique_snippets_list.query=' +s.query)
                if (s.link not in name_links) and (s.link not in geo_links) and (s.link not in orgs_links) and (s.link not in topics_links):
                    continue
                if s.link in name_links and s.link in orgs_links and s.link in topics_links and s.link in geo_links:
                    convergent_4.append(s)
                    name_links.remove(s.link)
                    orgs_links.remove(s.link)
                    geo_links.remove(s.link)
                    topics_links.remove(s.link)
                elif (s.link in name_links) and (s.link in geo_links) and (s.link in orgs_links):
                    convergent_3.append(s)
                    name_links.remove(s.link)
                    geo_links.remove(s.link)
                    orgs_links.remove(s.link)
                elif (s.link in geo_links) and (s.link in orgs_links) and (s.link in topics_links):
                    convergent_3.append(s)
                    geo_links.remove(s.link)
                    orgs_links.remove(s.link)
                    topics_links.remove(s.link)
                elif (s.link in orgs_links) and (s.link in topics_links) and (s.link in name_links):
                    convergent_3.append(s)
                    orgs_links.remove(s.link)
                    topics_links.remove(s.link)
                    name_links.remove(s.link)
                elif (s.link in name_links) and (s.link in geo_links) and (s.link in topics_links):
                    convergent_3.append(s)
                    name_links.remove(s.link)
                    geo_links.remove(s.link)
                    topics_links.remove(s.link)
                elif (s.link in name_links) and (s.link in geo_links):
                    convergent_2.append(s)
                    name_links.remove(s.link)
                    geo_links.remove(s.link)
                elif (s.link in name_links) and (s.link in orgs_links):
                    convergent_2.append(s)
                    name_links.remove(s.link)
                    orgs_links.remove(s.link)
                elif (s.link in name_links) and (s.link in topics_links):
                    convergent_2.append(s)
                    name_links.remove(s.link)
                    topics_links.remove(s.link)
                elif (s.link in geo_links) and (s.link in orgs_links):
                    convergent_2.append(s)
                    geo_links.remove(s.link)
                    orgs_links.remove(s.link)
                elif (s.link in geo_links) and (s.link in topics_links):
                    convergent_2.append(s)
                    geo_links.remove(s.link)
                    topics_links.remove(s.link)
                elif (s.link in orgs_links) and (s.link in topics_links):
                    convergent_2.append(s)
                    orgs_links.remove(s.link)
                    topics_links.remove(s.link)
                elif (s.link in name_links):
                    convergent_1.append(s)
                    name_links.remove(s.link)
                elif (s.link in geo_links):
                    convergent_1.append(s)
                    geo_links.remove(s.link)
                elif (s.link in orgs_links):
                    convergent_1.append(s)
                    orgs_links.remove(s.link)
                elif (s.link in topics_links):
                    convergent_1.append(s)
                    topics_links.remove(s.link)

            r.stop()


            unique_link_set = set([])
            unique_convergent_4 = set([])
            unique_convergent_3 = set([])
            unique_convergent_2 = set([])
            unique_convergent_1 = set([])
            repeated = set([])



            for s in convergent_4:
                if s.link not in unique_link_set:
                    unique_link_set.add(s.link)
                    unique_convergent_4.add(s)
                    logging.debug ('convergent_4 snippet=' +s.query+ ' title= ' +s.title+ ' ==> ' +s.link)
                else:
                    repeated.add(s)
                    logging.debug ('repeated_4 snippet=' +s.query+ ' title= ' +s.title+ ' ==> ' +s.link)

            ps4 = PipelineStats()
            ps4.type = 'converging pipelines 4'
            diaspora_output.write_converging_pipeline(ps4, list(unique_convergent_4), 4)

            for s in convergent_3:
                if s.link not in unique_link_set:
                    unique_link_set.add(s.link)
                    unique_convergent_3.add(s)
                    logging.debug ('convergent_3 snippet=' +s.query+ ' title= ' +s.title+ ' ==> ' +s.link)
                else:
                    repeated.add(s)
                    logging.debug ('repeated_3 snippet=' +s.query+ ' title= ' +s.title+ ' ==> ' +s.link)

            ps3 = PipelineStats()
            ps3.type = 'converging pipelines 3'
            diaspora_output.write_converging_pipeline(ps3, list(unique_convergent_3), 3)


            for s in convergent_2:
                if s.link not in unique_link_set:
                    unique_link_set.add(s.link)
                    unique_convergent_2.add(s)
                    logging.debug ('convergent_2 snippet=' +s.query+ ' title= ' +s.title+ ' ==> ' +s.link)
                else:
                    repeated.add(s)
                    logging.debug ('repeated_2 snippet=' +s.query+ ' title= ' +s.title+ ' ==> ' +s.link)

            ps2 = PipelineStats()
            ps2.type = 'converging pipelines 2'
            diaspora_output.write_converging_pipeline(ps2, list(unique_convergent_2), 2)


            for s in convergent_1:
                if s.link not in unique_link_set:
                    unique_link_set.add(s.link)
                    unique_convergent_1.add(s)
                    logging.debug ('convergent_1 snippet=' +s.query+ ' title= ' +s.title+ ' ==> ' +s.link)
                else:
                    repeated.add(s)
                    logging.debug ('repeated_1 snippet=' +s.query+ ' title= ' +s.title+ ' ==> ' +s.link)


            ps1 = PipelineStats()
            ps1.type = 'converging pipelines 1'
            diaspora_output.write_converging_pipeline(ps1, list(unique_convergent_1), 1)
            diaspora_output.close_person()
            # END COMMENT CONVERGING PIPELINES


#*******************************************************
#             WRITE TO DATABASE
#*******************************************************

            
            if nombre_busqueda.isdigit():
                #todo: update process status, processed/total
                person_id = diaspora_output.write_person_to_db('update', int(nombre_busqueda), db_busqueda, \
                                                               filter_value, user, description)
                if not person_id:
                    logging.error("Can't update persons database")
                    continue
                
            #FETCHING PERSON FROM DATABASE
            p = Persona.objects.get(id=person_id)

            
#*******************************************************
#             FEATURE ANNOTATION
#*******************************************************

            
            logging.info("processing snippet features for person " +p.name)
            #name in http pre-snippet cycle tests
            name_tokens = re.split('[ \-]', p.name)
            name_test = []
            for token in name_tokens:
                name = token.strip()
                if len(name)>2 and name not in ('del', 'von', 'DEL', 'xoVON'):
                    name_test.append(name)
            for s in p.snippet_set.all():
                title_test_str = s.title.encode('utf-8')
                descr_test_str = s.description.encode('utf-8')
                link_test_str = s.link.encode('utf-8')
                if s.RE_features is None:
                    s.RE_features = 0
                if BlacklistHttpRegex.test(link_test_str):
                    logging.debug ('FOUND blacklist REGEX IN HTTP:\n ' +s.link)
                    s.RE = 1
                    s.save()
                    continue
 
                if OrganizationRegex.test(title_test_str):
                    logging.debug ('FOUND ORGANIZATION IN TITLE:\n ' +s.title)
                    s.RE_features |= 1
                if OrganizationRegex.test(descr_test_str):
                    logging.debug('FOUND ORGANIZATION IN DESCR:\n ' +s.description)
                    s.RE_features |= 1

                snippet_countries = []
                countries = CountryGazet.typed_list_test(title_test_str)
                if len(countries)>0:
                    logging.debug ('FOUND COUNTRY IN TITLE:\n ' +s.title)
                    s.RE_features |= 2
                    snippet_countries += countries
                countries = CountryGazet.typed_list_test(descr_test_str)
                if len(countries)>0:
                    logging.debug('FOUND COUNTRY IN DESCR:\n ' +s.description)
                    s.RE_features |= 2
                    snippet_countries += countries
                countries = CountryGazetCase.typed_list_test(title_test_str)
                if len(countries)>0:
                    logging.debug ('FOUND COUNTRY IN TITLE:\n ' +s.title)
                    s.RE_features |= 2
                    snippet_countries += countries
                countries = CountryGazetCase.typed_list_test(descr_test_str)
                if len(countries)>0:
                    logging.debug('FOUND COUNTRY IN DESCR:\n ' +s.description)
                    s.RE_features |= 2
                    snippet_countries += countries
                countries = CityGazetCase.typed_list_test(title_test_str)
                if len(countries)>0:
                    logging.debug ('FOUND CITY IN TITLE:\n ' +s.title)
                    s.RE_features |= 4
                    snippet_countries += countries
                countries = CityGazetCase.typed_list_test(descr_test_str)
                if len(countries)>0:
                    logging.debug('FOUND CITY IN DESCR:\n ' +s.description)
                    s.RE_features |= 4
                    snippet_countries += countries
                countries = CityGazet.typed_list_test(title_test_str)
                if len(countries)>0:
                    logging.debug ('FOUND CITY IN TITLE:\n ' +s.title)
                    s.RE_features |= 4
                    snippet_countries += countries
                countries = CityGazet.typed_list_test(descr_test_str)
                if len(countries)>0:
                    logging.debug('FOUND CITY IN DESCR:\n ' +s.description)
                    s.RE_features |= 4
                    snippet_countries += countries
                if len(snippet_countries)>0:
                    snippet_countries = list(set(snippet_countries))
                    logging.debug('SNIPPET_COUNTRIES = '+str(snippet_countries))
                    s.featured_countries = str(snippet_countries).replace('[','').replace(']','').replace("'","").replace(' ','')
                    
                if AccronymGazet.test(title_test_str):
                    logging.debug ('FOUND ACCRONYM IN TITLE:\n ' +s.title)
                    s.RE_features |= 8
                if AccronymGazet.test(descr_test_str): 
                    logging.debug('FOUND ACCRONYM IN DESCR:\n ' +s.description)
                    s.RE_features |= 8
                if BiophrasesRegex.test(title_test_str):
                    logging.debug ('FOUND BIOGRAPHICAL PHRASE IN TITLE:\n ' +s.title)
                    s.RE_features |= 16
                if BiophrasesRegex.test(descr_test_str): 
                    logging.debug('FOUND BIOGRAPHICAL PHRASE IN DESCR:\n ' +s.description)
                    s.RE_features |= 16
                if ProfessionRegex.test(title_test_str):
                    logging.debug ('FOUND PROFESSION REGEX IN TITLE:\n ' +s.title)
                    s.RE_features |= 32
                if ProfessionRegex.test(descr_test_str): 
                    logging.debug('FOUND PROFESSION REGEX IN DESCR:\n ' +s.description)
                    s.RE_features |= 32
                if ProfessionGazt.test(title_test_str):
                    logging.debug ('FOUND PROFESSION GAZT IN TITLE:\n ' +s.title)
                    s.RE_features |= 32
                if ProfessionGazt.test(descr_test_str): 
                    logging.debug('FOUND PROFESSION GAZT IN DESCR:\n ' +s.description)
                    s.RE_features |= 32
                if DegreeRegex.test(title_test_str):
                    logging.debug ('FOUND DEGREE REGEX IN TITLE:\n ' +s.title)
                    s.RE_features |= 64
                if DegreeRegex.test(descr_test_str): 
                    logging.debug('FOUND DEGREE REGEX IN DESCR:\n ' +s.description)
                    s.RE_features |= 64
                if DegreeGazt.test(title_test_str):
                    logging.debug ('FOUND DEGREE GAZT IN TITLE:\n ' +s.title)
                    s.RE_features |= 64
                if DegreeGazt.test(descr_test_str): 
                    logging.debug('FOUND DEGREE GAZT IN DESCR:\n ' +s.description)
                    s.RE_features |= 64
                if CvRegex.test(title_test_str):
                    logging.debug ('FOUND CV GENERAL REGEX IN TITLE:\n ' +s.title)
                    s.RE_features |= 128
                if CvRegex.test(descr_test_str): 
                    logging.debug('FOUND CV GENERAL REGEX IN DESCR:\n ' +s.description)
                    s.RE_features |= 128
                if CvHttpRegex.test(link_test_str):
                    logging.debug ('FOUND CV HTTP REGEX IN HTTP:\n ' +s.link)
                    s.RE_features |= 128
                if CvHttpRegex.test(title_test_str): 
                    logging.debug('FOUND CV HTTP REGEX  IN TITLE:\n ' +s.title)
                    s.RE_features |= 128
                #name in http feature
                for test in name_test:
                    re_object = re.search(test,link_test_str,flags=re.IGNORECASE)
                    if re_object:
                        logging.debug('FOUND NAME ' +test+ ' IN HTTP LINK:\n' \
                                      +link_test_str)
                        s.RE_features |= 256
                        break
                if LatinNatRegex.test(title_test_str):
                    logging.debug ('FOUND latin american nationality REGEX IN TITLE:\n ' +s.title)
                    s.RE_features |= 512
                if LatinNatRegex.test(descr_test_str): 
                    logging.debug('FOUND latin american nationality REGEX IN DESCR:\n ' +s.description)
                    s.RE_features |= 512      
                if WorldNatRegex.test(title_test_str):
                    logging.debug ('FOUND non latin american nationality REGEX IN TITLE:\n ' +s.title)
                    s.RE_features |= 1024
                if WorldNatRegex.test(descr_test_str): 
                    logging.debug('FOUND non latin american nationality REGEX IN DESCR:\n ' +s.description)
                    s.RE_features |= 1024
                if WorldNatGazt.test(title_test_str):
                    logging.debug ('FOUND non latin american nationality GAZT IN TITLE:\n ' +s.title)
                    s.RE_features |= 1024
                if WorldNatGazt.test(descr_test_str): 
                    logging.debug('FOUND non latin american nationality GAZT IN DESCR:\n ' +s.description)
                    s.RE_features |= 1024
                if EmailRegex.test(title_test_str):
                    logging.debug ('FOUND email REGEX IN TITLE:\n ' +s.title)
                    s.RE_features |= 2048
                if EmailRegex.test(descr_test_str): 
                    logging.debug('FOUND email REGEX IN DESCR:\n ' +s.description)
                    s.RE_features |= 2048
                if PublicationRegex.test(title_test_str):
                    logging.debug ('FOUND PUBLICATION REGEX IN TITLE:\n ' +s.title)
                    s.RE_features |= 4096
                if PublicationRegex.test(descr_test_str): 
                    logging.debug('FOUND PUBLICATION REGEX IN DESCR:\n ' +s.description)
                    s.RE_features |= 4096
                if PublicationHttpRegex.test(link_test_str):
                    logging.debug ('FOUND PUBLICATION HTTP IN LINK:\n ' +s.title)
                    s.RE_features |= 4096
                re_object = linked_re.search(link_test_str)
                if re_object:
                    logging.debug ('FOUND LinkedIn address IN LINK:\n ' \
                                   +link_test_str)
                    s.RE_features |= 8192
                if TesisHttpRegex.test(link_test_str):
                    logging.debug ('FOUND TESIS HTTP IN LINK:\n ' +s.title)
                    s.RE_features |= 16384 
                if TesisRegex.test(title_test_str):
                    logging.debug ('FOUND TESIS REGEX IN TITLE:\n ' +s.title)
                    s.RE_features |= 16384
                if TesisRegex.test(descr_test_str): 
                    logging.debug('FOUND TESIS REGEX IN DESCR:\n ' +s.description)
                    s.RE_features |= 16384
                #blacklist annotation RE field = 1
                s.converging_pipelines = 0
                s.save()


            
#*******************************************************
#             PERSON AND SNIPPET CLASSIFICATION
#*******************************************************


            data_model_file = UNOPORUNO_ROOT + '/resources/classifiers/smo/models/weka.classifiers.functions.SMO.data.model'
            #self.classify_person_top5(p, output_folder,'weka.classifiers.functions.SMO',data_model_file, DiasporaOutput)
            persona = p
            output_path = output_folder

            
    #def classify_person_top5(self, persona, path, classifier, data_model_file, diasporaOutput):    
        #TODO: validar cuando a) no hay snippets clasificados como positivos y b) hay menos de 5 snippets clasificados como positivos
    
            logging.info('classifying persons with weka.classifiers.functions.SMO.data.model and persona_id='+str(persona.id)+' +data_model_file' +data_model_file)
            try:
                base = DiasporaOutput(output_path)
            except:
                logging.error('Error on output path:'+output_path)
                return False
            classifier = 'weka.classifiers.functions.SMO'
            d_personas = dict()
            persona_file = base.write_personal_feature_matrix_2class(persona)
            command = 'java ' +classifier+ ' -l '+data_model_file+' -T '+persona_file+' -p 1 > '+persona_file+'.out'
            try:
                result = os.system(command)
            except:
                logging.error('Error creating weka file with command='+command)
                return False

            logging.info('classyfying with command=' + command)

            for subdirs, dirs, files in os.walk(output_path):
                for file in files:
                    re_out = re.search('\.out$', file)
                    if not re_out:
                        continue
                    classed_snippets = self.get_weka_top5(output_path+'/'+file)
                    logging.info('Extracting ' +str(len(classed_snippets))+ ' tuples from file:' +file ) 
                    logging.info('Classed snippets=' +str(classed_snippets))
                    if len(classed_snippets):
                        for tupla in classed_snippets:
                            logging.info('looking for snippet id =' +str(tupla[0]))
                            snippet = Snippet.objects.get(id=int(tupla[0]))
                            if d_personas.has_key(snippet.persona_id):
                                d_paises = d_personas[snippet.persona_id]
                            else:
                                d_paises = dict()
                            lista_paises = snippet.featured_countries.split(',') if snippet.featured_countries else []
                            for pais in lista_paises:
                                u_pais = pais.encode('utf-8')
                                if d_paises.has_key(u_pais):
                                    d_paises[u_pais] += 1
                                else:
                                    d_pais = dict({u_pais:1})
                                    d_paises.update(d_pais)
                            d_persona = dict({snippet.persona_id:d_paises})
                            d_personas.update(d_persona)

                            snippet.converging_pipelines=2
                            snippet.RE_score = self.get_feature_count(snippet.RE_features)
                            snippet.save()

            LA = ['AR','BZ','BO','CL','CO','CR','C','DO','SV','MX','GT','HT','JM','NI','PY','PE','VE','TT','PY','HN','PA','UY']

            if not d_personas.has_key(persona.id):                      
                d_paises = dict()
                d_persona = dict({persona.id:d_paises})
                d_personas.update(d_persona)

            logging.info('Persona ' +persona.name+ ' has the following country frequencies:' +str(d_personas[persona.id])+ \
                         ' and prediction='+str(persona.prediction))
            LA_freq = ('',0)
            mundo_freq = ('',0)
            for pais in d_personas[persona.id].keys():
                u_pais = pais.encode('utf-8')            
                if u_pais in LA:
                    if d_personas[persona.id][u_pais] > LA_freq[1]:
                        LA_freq = (u_pais,d_personas[persona.id][u_pais])
                else:
                    if d_personas[persona.id][u_pais] > mundo_freq[1]:
                        mundo_freq = (u_pais, d_personas[persona.id][u_pais])
            logging.info('Pais LA mas frequente:' +str(LA_freq))
            logging.info('Pais no LA mas frequente:' +str(mundo_freq))

            #3 del país móvil más frecuente
            #2 del país latinoamericano más frecuente
            #los demás con móviles
            if mundo_freq[1]>0 and LA_freq[1]>0:
                persona.prediction=1
                logging.info(persona.name+' is movil! with prediction=' +str(persona.prediction))            
            elif mundo_freq[1]>0 or LA_freq[1]>0:
                persona.prediction = 2
                logging.info('local!')
            else:
                persona.prediction = 3
                logging.info('no sé!')


            mobile_snippets = persona.snippet_set.filter(converging_pipelines=2).order_by('-RE_score')
            local_snippets = persona.snippet_set.filter(converging_pipelines=3).order_by('-RE_score')    
            converging_count = [0,0,0] #[converging_count, world_count, LA_count]
            if mundo_freq[1]>0:
                mobile_limit = min(3,mundo_freq[1])
                LA_limit = min(2,LA_freq[1])
                for s in mobile_snippets:
                    if converging_count[0]>=5:
                        break
                    if converging_count[1]<mobile_limit:
                        if mundo_freq[0] in str(s.featured_countries):
                            s.converging_pipelines=1
                            s.save()
                            converging_count[0]+=1
                            converging_count[1]+=1
                            logging.info('world hit!')
                    elif converging_count[2]<LA_limit:
                        if LA_freq[0] in str(s.featured_countries):
                            s.converging_pipelines=1
                            s.save()
                            converging_count[0]+=1
                            converging_count[2]+=1
                            logging.info('LA hit!')
                if converging_count[0]<5:
                    for s in local_snippets:
                        if converging_count[0]>=5:
                            break
                        if converging_count[1]<mobile_limit:
                            if mundo_freq[0] in str(s.featured_countries):
                                s.converging_pipelines=1
                                s.save()
                                converging_count[0]+=1
                                converging_count[1]+=1
                                logging.info('world local hit!')
                        elif converging_count[2]<LA_limit:
                            if LA_freq[0] in str(s.featured_countries):
                                s.converging_pipelines=1
                                s.save()
                                converging_count[0]+=1
                                converging_count[2]+=1
                                logging.info('LA local hit!')
            if converging_count[0]<5:
                for s in mobile_snippets:
                    if converging_count[0]>=5:
                        break
                    if s.converging_pipelines==1:
                        continue
                    s.converging_pipelines=1
                    s.save()
                    converging_count[0]+=1
            if converging_count[0]<5:
                for s in local_snippets:
                    if converging_count[0]>=5:
                        break
                    if s.converging_pipelines==1:
                        continue
                    s.converging_pipelines=1
                    s.save()
                    converging_count[0]+=1
            if converging_count[0]<5:
                todos = persona.snippet_set.filter(FG=1).exclude(RE=1).order_by('-RE_features')
                for s in local_snippets:
                    if converging_count[0]>=5:
                        break
                    if s.converging_pipelines==1:
                        continue
                    s.converging_pipelines=1
                    s.save()
                    converging_count[0]+=1
            if converging_count<5:
                for s in local_snippets:
                    if converging_count>=5:
                        break
                    s.converging_pipelines=1
                    s.save()
                    converging_count +=1
            logging.info(persona.name+' is movil! with prediction=' +str(persona.prediction))
            persona.save()

            
#*******************************************************
#             TOP N FREQUENCY ANALYSIS
#*******************************************************

            logging.info("starting frequency analysis for person " +persona.name)
            person_countries = []
            person_organizations = []
            top_snippets_count = 0
            persona.vinculo_set.all().delete()
            for s in persona.snippet_set.filter(FG=1).exclude(RE=1).filter(converging_pipelines=1):
                if s.FG==0 or s.RE_features<1:
                    continue
                title_test_str = s.title.encode('utf-8')
                descr_test_str = s.description.encode('utf-8')
                #todo filtrar los snippets de acuerdo a las features que buscamos
                snippet_countries = []
                snippet_organizations = []
                orgs = OrganizationRegex.list_test(title_test_str)
                if len(orgs)>0:
                    logging.debug ('FOUND ORGANIZATIONS ' +str(orgs)+' IN TITLE:\n ' +s.title)
                    snippet_organizations += orgs
                orgs = OrganizationRegex.list_test(descr_test_str)
                if len(orgs)>0:
                    logging.debug('FOUND ORGANIZATIONS ' +str(orgs)+ ' IN DESCR:\n ' +s.description)
                    snippet_organizations += orgs
                accronyms = AccronymGazet.list_test(title_test_str)
                if len(accronyms)>0:
                    logging.debug('FOUND ORG.ACCRONYMS ' +str(accronyms)+ ' IN TITLE:\n ' +s.title)
                    snippet_organizations += accronyms
                accronyms = AccronymGazet.list_test(descr_test_str)
                if len(accronyms)>0:
                    logging.debug('FOUND ORG.ACCRONYMS ' +str(accronyms)+ ' IN TITLE:\n ' +s.description)
                    snippet_organizations += accronyms                
                countries = CountryGazet.list_test(title_test_str)
                if len(countries)>0:
                    logging.debug ('FOUND COUNTRIES '+str(countries)+' IN TITLE:\n ' +s.title)
                    snippet_countries += countries
                countries = CountryGazet.list_test(descr_test_str)
                if len(countries)>0:
                    logging.debug('FOUND COUNTRIES '+str(countries)+' IN DESCR:\n ' +s.description)
                    snippet_countries += countries
                countries = CountryGazetCase.list_test(title_test_str)
                if len(countries)>0:
                    logging.debug ('FOUND COUNTRIES '+str(countries)+' IN TITLE:\n ' +s.title)
                    snippet_countries += countries
                countries = CountryGazetCase.list_test(descr_test_str)
                if len(countries):
                    logging.debug('FOUND COUNTRIES '+str(countries)+' IN DESCR:\n ' +s.description)
                    snippet_countries += countries
                countries = CityGazet.list_test(title_test_str)
                if len(countries)>0:
                    logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CI TITLE\n' +s.title)
                    snippet_countries += countries
                countries = CityGazet.list_test(descr_test_str)
                if len(countries)>0:
                    logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CI DESCRIPTION\n' +s.description)
                    snippet_countries += countries
                countries = CityGazetCase.list_test(title_test_str)
                if len(countries)>0:
                    logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CD TITLE\n' +s.title)
                    snippet_countries += countries        
                countries = CityGazetCase.list_test(descr_test_str)
                if len(countries)>0:
                    logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CD DESCRIPTION\n' +s.description)
                    snippet_countries += countries
                person_countries += snippet_countries
                person_organizations += snippet_organizations
                top_snippets_count += 1
                if top_snippets_count in (5,10,15,20):
                    dict_org = self.construye_dict_freq(person_organizations)
                    dict_loc = self.construye_dict_freq(person_countries)
                    list_org = dict_org.items()
                    list_loc = dict_loc.items()
                    sorted_list_org = sorted(list_org, key=lambda t:-t[1])
                    sorted_list_loc = sorted(list_loc, key=lambda t:-t[1])
                    organizations_str = ''
                    locations_str = ''
                    for e in sorted_list_org:
                        #logging.debug('type e='+str(type(e))+ ',type e[0]'+str(type(e[0]))+',e='+str(e))
                        organizations_str += e[0] + ' (' + str(e[1]) + ')\n' if len(e)>1 else ''
                    for e in sorted_list_loc:
                        locations_str += e[0] + ' (' + str(e[1]) + ')\n' if len(e)>1 else ''

                    logging.info('VÍNCULOS ORGANIZACIONES:: '+str(sorted_list_org))
                    vinculo = Vinculo()
                    vinculo.persona = p
                    vinculo.organizaciones = organizations_str
                    logging.info('VÍNCULOS LUGARES:: '+str(sorted_list_loc))
                    vinculo.lugares = locations_str
                    vinculo.descripcion = 'Top ' + str(top_snippets_count)
                    vinculo.tipo = top_snippets_count
                    vinculo.save()

            if top_snippets_count >= 20:
                continue

            for s in persona.snippet_set.filter(FG=1).exclude(RE=1).exclude(converging_pipelines=1).order_by('-RE_score'):
                if s.FG==0 or s.RE_features<1:
                    continue
                title_test_str = s.title.encode('utf-8')
                descr_test_str = s.description.encode('utf-8')
                #todo filtrar los snippets de acuerdo a las features que buscamos
                snippet_countries = []
                snippet_organizations = []
                orgs = OrganizationRegex.list_test(title_test_str)
                if len(orgs)>0:
                    logging.debug ('FOUND ORGANIZATIONS ' +str(orgs)+' IN TITLE:\n ' +s.title)
                    snippet_organizations += orgs
                orgs = OrganizationRegex.list_test(descr_test_str)
                if len(orgs)>0:
                    logging.debug('FOUND ORGANIZATIONS ' +str(orgs)+ ' IN DESCR:\n ' +s.description)
                    snippet_organizations += orgs
                accronyms = AccronymGazet.list_test(title_test_str)
                if len(accronyms)>0:
                    logging.debug('FOUND ORG.ACCRONYMS ' +str(accronyms)+ ' IN TITLE:\n ' +s.title)
                    snippet_organizations += accronyms
                accronyms = AccronymGazet.list_test(descr_test_str)
                if len(accronyms)>0:
                    logging.debug('FOUND ORG.ACCRONYMS ' +str(accronyms)+ ' IN TITLE:\n ' +s.description)
                    snippet_organizations += accronyms                
                countries = CountryGazet.list_test(title_test_str)
                if len(countries)>0:
                    logging.debug ('FOUND COUNTRIES '+str(countries)+' IN TITLE:\n ' +s.title)
                    snippet_countries += countries
                countries = CountryGazet.list_test(descr_test_str)
                if len(countries)>0:
                    logging.debug('FOUND COUNTRIES '+str(countries)+' IN DESCR:\n ' +s.description)
                    snippet_countries += countries
                countries = CountryGazetCase.list_test(title_test_str)
                if len(countries)>0:
                    logging.debug ('FOUND COUNTRIES '+str(countries)+' IN TITLE:\n ' +s.title)
                    snippet_countries += countries
                countries = CountryGazetCase.list_test(descr_test_str)
                if len(countries):
                    logging.debug('FOUND COUNTRIES '+str(countries)+' IN DESCR:\n ' +s.description)
                    snippet_countries += countries
                countries = CityGazet.list_test(title_test_str)
                if len(countries)>0:
                    logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CI TITLE\n' +s.title)
                    snippet_countries += countries
                countries = CityGazet.list_test(descr_test_str)
                if len(countries)>0:
                    logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CI DESCRIPTION\n' +s.description)
                    snippet_countries += countries
                countries = CityGazetCase.list_test(title_test_str)
                if len(countries)>0:
                    logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CD TITLE\n' +s.title)
                    snippet_countries += countries        
                countries = CityGazetCase.list_test(descr_test_str)
                if len(countries)>0:
                    logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CD DESCRIPTION\n' +s.description)
                    snippet_countries += countries
                person_countries += snippet_countries
                person_organizations += snippet_organizations
                top_snippets_count += 1
                if top_snippets_count in (5,10,15,20):
                    dict_org = self.construye_dict_freq(person_organizations)
                    dict_loc = self.construye_dict_freq(person_countries)
                    list_org = dict_org.items()
                    list_loc = dict_loc.items()
                    sorted_list_org = sorted(list_org, key=lambda t:-t[1])
                    sorted_list_loc = sorted(list_loc, key=lambda t:-t[1])
                    organizations_str = ''
                    locations_str = ''
                    for e in sorted_list_org:
                        #logging.debug('type e='+str(type(e))+ ',type e[0]'+str(type(e[0]))+',e='+str(e))
                        organizations_str += e[0] + ' (' + str(e[1]) + ')\n' if len(e)>1 else ''
                    for e in sorted_list_loc:
                        locations_str += e[0] + ' (' + str(e[1]) + ')\n' if len(e)>1 else ''

                    logging.info('VÍNCULOS ORGANIZACIONES:: '+str(sorted_list_org))
                    vinculo = Vinculo()
                    vinculo.persona = p
                    vinculo.organizaciones = organizations_str
                    logging.info('VÍNCULOS LUGARES:: '+str(sorted_list_loc))
                    vinculo.lugares = locations_str
                    vinculo.descripcion = 'Top ' + str(top_snippets_count)
                    vinculo.tipo = top_snippets_count
                    vinculo.save()

                if top_snippets_count >= 20:
                    break

#*******************************************************
#             UPDATE PROGRESS RECORD
#*******************************************************
            personas_procesadas += 1
            nueva_busqueda.status = '@' +str(personas_procesadas) +'/'+ str(len(personas))
            nueva_busqueda.save()
        nueva_busqueda.status = 'OK'
        nueva_busqueda.save()
        
            

    def construye_dict_freq(self,lista):
        d = dict()
        logging.debug('len lista=' +str(len(lista)))
        for e in lista:
            if d.has_key(e):
                d[e] += 1
            else:
                d_tmp = dict({e:1})
                d.update(d_tmp)
                logging.debug('len dictionary='+str(len(d)))
        return d





    def get_weka_top5(self, file_name):
        logging.info('extracting top 5 from ' +file_name)
        strong_evidence = []
        try:
            f=open(file_name, 'r')
        except:
            return strong_evidence
        for line in f:
            columns = re.split(' +', line.strip())
            if len(columns)>1:
                if columns[2]=='2:1':
                    if columns[3]=='+':
                        #print columns
                        prediction = float(columns[4])
                        snippet_id = re.sub('[()]','',columns[5])
                    #else:
                    #    prediction = float(columns[3])
                    #    snippet_id = re.sub('[()]','',columns[4])
                        tupla = (snippet_id, prediction)
                        strong_evidence.append(tupla)
        ord_tuplas = sorted(strong_evidence, key=lambda t:-t[1])[:5]
        #TODO: si son menos de 5, completar con el resto
        return ord_tuplas



    def clean_busqueda(self, test_busqueda):
        command = 'python ' +UNOPORUNO_ROOT+ '/scripts/clean_converging_pipelines.py ' + test_busqueda
        if os.system(command)<0:
            logging.error("Couldn't clean_converging_pipelines")
            exit(-1)

    def get_feature_count(self,str_features):
        RE_features = str(bin(int(str_features))).replace('0b','')
        features = str(RE_features.zfill(15))
        feature_count=0
        for c in features:
            feature_count += 1 if c=='1' else 0
        return feature_count



        

        
class reloj:
    def __init__(self):
        self._start = time.time()
        self._stop = time.time()

    def stop(self):
        self._stop = time.time()

    def start(self):
        self._start = time.time()

    def tiempo(self):
        execution_time_sec = self._stop - self._start
        if execution_time_sec>60:
            execution_time_min = int(execution_time_sec/60)
            execution_time_sec = int(execution_time_sec%60)
        else:
            execution_time_min = 0
        if execution_time_min>60:
            execution_time_hrs = int(execution_time_min/60)
            execution_time_min = int(execution_time_min%60)
        else:
            execution_time_hrs = 0
        execution_time_sec = round(execution_time_sec)
        tiempo_str = str(execution_time_hrs)+ ':' +str(execution_time_min)+ ':' +str(int(execution_time_sec))
        return (execution_time_sec, tiempo_str)

class PipelineStats:
    def __init__(self):
        self.type = ''
        self.total_queries = 0
        self.total_snippets = 0
        self.tiempo_proceso = 0.0
        self.encontro_vinculo = False

class FilterStats:
    def __init__(self):
        self.type = ''
        self.seconds = 0.0


