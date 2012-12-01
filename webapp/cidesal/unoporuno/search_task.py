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
    def __init__(self, nombre, archivo, usuario, descripcion=''):
        self.arg_input_file = archivo
        self.arg_output_folder = archivo +'.'+ usuario
        self.arg_research_name = nombre
        self.arg_FG_sel = 'True'
        self.arg_users = usuario
        self.arg_description = descripcion


        logging.basicConfig(level=logging.INFO)
        config = ConfigParser.ConfigParser()
        config.read("unoporuno.conf")
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
        from busqueda_db.busqueda_db import Busqueda_DB


        if not CIDESAL_WEBAPP_PATH in sys.path:
            sys.path.append(CIDESAL_WEBAPP_PATH)
            sys.path.append(CIDESAL_WEBAPP_PATH+'cidesal/')
        from unoporuno.models import Busqueda, Persona, Snippet

        buscador = BuscadorDiasporas()

        personas_file = PersonasInput()
        personas_file.open_csv(self.arg_input_file)
        output_folder = self.arg_output_folder
        personas = personas_file.read()
        

        nombre_busqueda = self.arg_research_name
        filter_value = self.arg_FG_sel
        logging.debug(' filter_value' +filter_value)
        user = self.arg_users
        description = self.arg_description


        for p in personas:
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

            #********
            # NEW PIPELINE convergent
            #********
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
            db_busqueda = Busqueda_DB(UNOPORUNO_ROOT)
            if nombre_busqueda.isdigit():
                diaspora_output.write_to_db('update', int(nombre_busqueda), db_busqueda, filter_value, user, description)
            else:
                busqueda_id = diaspora_output.write_to_db('new', nombre_busqueda, db_busqueda, filter_value, user, description)
                nombre_busqueda = str(busqueda_id)
        
class PersonasInput:
    def __init__(self):
        self._re_a=re.compile(u'[áâä]')
        self._re_e=re.compile(u'[éèêë]')
        self._re_i=re.compile(u'[íïîì]')
        self._re_o=re.compile(u'[óòôö]')
        self._re_u=re.compile(u'[úùüû]')
        self._re_n=re.compile(u'[ñ]')
        self._re_A=re.compile(u'[ÁÀÄÂ]')
        self._re_E=re.compile(u'[ÉÈÊË]')
        self._re_I=re.compile(u'[ÍÌÏÎ]')
        self._re_O=re.compile(u'[ÓÒÔÖ]')
        self._re_U=re.compile(u'[ÚÙÛÜ]')
        self._re_N=re.compile(u'[Ñ]')
        


    def open_csv(self, input_file):
        self.read = self._read_csv
        self._input_csv = open(input_file)

    def _read_csv(self):
        global COLUMN_SEPARATOR
        personas_list = []
        for line in self._input_csv:
            clean_line = self._limpia_acentos(line)            
            columnas = clean_line.split(COLUMN_SEPARATOR)
            tamano = len(columnas)
            if tamano == ROW_SIZE:
                if columnas[0] and columnas[1]:
                    p = Persona(columnas[0], columnas[1], columnas[2], \
                            columnas[3], columnas[4], columnas[5])
                    personas_list.append(p)
                else:
                    logging.error('No name or id in row ' + clean_line)
            elif tamano == (ROW_SIZE-1):
                if columnas[0] and columnas[1]:
                    p = Persona(columnas[0], columnas[1], columnas[2], \
                            columnas[3], columnas[4])
                    personas_list.append(p)
                else:
                    logging.error('No name or id in row ' + clean_line)
            else:
                logging.error ('Bad csv row size, '+ str(tamano)+ ' columns expected')
        return personas_list

    #TODO: support propper UTF-8 with NLTK!!!
    def _limpia_acentos(self, linea):
        linea_u = unicode(linea, 'utf-8')
        linea_u = self._re_a.subn('a',linea_u)[0]
        linea_u = self._re_e.subn('e',linea_u)[0]
        linea_u = self._re_i.subn('i',linea_u)[0]
        linea_u = self._re_o.subn('o',linea_u)[0]
        linea_u = self._re_u.subn('u',linea_u)[0]
        linea_u = self._re_n.subn('n',linea_u)[0]
        linea_u = self._re_A.subn('A',linea_u)[0]
        linea_u = self._re_E.subn('E',linea_u)[0]
        linea_u = self._re_I.subn('I',linea_u)[0]
        linea_u = self._re_O.subn('O',linea_u)[0]
        linea_u = self._re_U.subn('U',linea_u)[0]
        linea_u = self._re_N.subn('N',linea_u)[0]
        linea_a = linea_u.encode('ascii', 'ignore')
        return linea_a
        
        
        
class Persona:
    def __init__(self, id, nom, tem='', org='', lug='', vin=''):
        self.id = id.strip()
        self.nombre = nom.strip()
        self.temas = tem.strip()
        self.orgs = org.strip()
        self.lugares = lug.strip()
        self.vinculo = vin.strip()


class DiasporaOutput:
    def __init__(self, output_path):
        self._output_path = output_path + '/'
        self._xml_buffer = ''
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        self.file_name = ''

    def open_person(self, persona):
        self._xml_file = self._create_person_file(persona.id, persona.nombre)
        print >> self._xml_file, '\t<person id="' +self._clean_xml(persona.id) + '">'
        print >> self._xml_file, '\t<name>' +self._clean_xml(persona.nombre)+ '</name>'
        print >> self._xml_file, '\t<topics>' +self._clean_xml(persona.temas)+ '</topics>'
        print >> self._xml_file, '\t<orgs>' +self._clean_xml(persona.orgs)+ '</orgs>'
        print >> self._xml_file, '\t<places>' +self._clean_xml(persona.lugares)+ '</places>'
        print >> self._xml_file, '\t<link>' +self._clean_xml(persona.vinculo)+ '</link>'


    def close_person(self):
        print >> self._xml_file, '</person>' 
        self._xml_file.close()

    
    def write_pipeline(self, pipeline, snippets_list):
        print >> self._xml_file, '<pipeline type="' +pipeline.type+ '">'
        print >> self._xml_file, '\t<stats>'
        print >> self._xml_file, '\t\t<total_queries>' +str(pipeline.total_queries)+ '</total_queries>'
        print >> self._xml_file, '\t\t<total_snippets>' +str(pipeline.total_snippets)+ '</total_snippets>'
        print >> self._xml_file, '\t\t<processing_time>' +str(pipeline.tiempo_proceso)+ '</processing_time>'
        print >> self._xml_file, '\t\t<link_found>' +str(pipeline.encontro_vinculo)+ '</link_found>'
        print >> self._xml_file, '\t</stats>'
        print >> self._xml_file, '\t<snippets>'
        logging.debug('PipelineStatus:: ps.snippets.type='+str(type(snippets_list)))
        logging.debug('PipelineStatus:: ps.snippets.len='+str(len(snippets_list)))
        for s in snippets_list:
            logging.debug('PipelineStatus:: adding to xml:' +s.title)
            print >> self._xml_file, '\t\t<snippet>'
            print >> self._xml_file, '\t\t<query>' +self._clean_xml(s.query)+ '</query>'
            print >> self._xml_file, '\t\t\t<title>' +self._clean_xml(s.title)+ '</title>'
            status = s.filter_status.vinculo_encontrado
            print >> self._xml_file, '\t\t\t<description>' +self._clean_xml(s.description)+ '</description>'
            print >> self._xml_file, '\t\t\t<link status="' +str(status)+ '">' +self._clean_xml(s.link)+ '</link>'
            print >> self._xml_file, '\t\t\t<engine>' +self._clean_xml(s.engine)+ '</engine>'

            
            FG = s.filter_status.nominal
            ESA = s.filter_status.semantic
            RE = s.filter_status.biographic
            print >> self._xml_file, '\t\t<filters FG="' +str(FG)+ '" ESA="' +str(ESA)+ '" RE="' +str(RE)+ '"/>'
            print >> self._xml_file, '\t\t</snippet>'
        print >> self._xml_file, '\t</snippets>'
        print >> self._xml_file, '\t</pipeline>' 

    def write_converging_pipeline(self, pipeline, snippets_list, converging_number):
        print >> self._xml_file, '<converging_pipelines number="' +str(converging_number)+ '">'
        print >> self._xml_file, '\t<stats>'
        print >> self._xml_file, '\t\t<total_snippets>' +str(pipeline.total_snippets)+ '</total_snippets>'
        print >> self._xml_file, '\t\t<link_found>' +str(pipeline.encontro_vinculo)+ '</link_found>'
        print >> self._xml_file, '\t</stats>'
        print >> self._xml_file, '\t<snippets>'
        logging.debug('PipelineStatus:: ps.snippets.type='+str(type(snippets_list)))
        logging.debug('PipelineStatus:: ps.snippets.len='+str(len(snippets_list)))
        for s in snippets_list:
            logging.debug('PipelineStatus:: adding to xml:' +s.title)
            print >> self._xml_file, '\t\t<snippet>'
            print >> self._xml_file, '\t\t<query>' +self._clean_xml(s.query)+ '</query>'
            print >> self._xml_file, '\t\t\t<title>' +self._clean_xml(s.title)+ '</title>'
            status = s.filter_status.vinculo_encontrado
            print >> self._xml_file, '\t\t\t<description>' +self._clean_xml(s.description)+ '</description>'
            print >> self._xml_file, '\t\t\t<link status="' +str(status)+ '">' +self._clean_xml(s.link)+ '</link>'
            print >> self._xml_file, '\t\t\t<query_type>' +s.query_type+ '</query_type>'

            
            FG = s.filter_status.nominal
            ESA = s.filter_status.semantic
            RE = s.filter_status.biographic
            print >> self._xml_file, '\t\t<filters FG="' +str(FG)+ '" ESA="' +str(ESA)+ '" RE="' +str(RE)+ '"/>'
            print >> self._xml_file, '\t\t</snippet>'
        print >> self._xml_file, '\t</snippets>'
        print >> self._xml_file, '</converging_pipelines>' 

    def write_to_db(self, write_type, nombre, db_busqueda, filter='All', user='', description=''):
        logging.debug('writing person file_name = ' +self.file_name+ ' to database')
        busqueda_id = 0
        if write_type == 'new':    
            busqueda_id = db_busqueda.new(nombre, filter, user, description)
            db_busqueda.update_person_from_file(self.file_name)
        elif write_type == 'update':
            db_busqueda.get(nombre, filter)
            db_busqueda.update_person_from_file(self.file_name)
        return busqueda_id
    

    def print_snippet_std(self, snippets_list):
        if len(snippets_list)>0:
            for s in snippets_list:
                print '--------------------------------'
                print '|SNIPPET_QUERY::', s.query
                print '|SNIPPET_TITLE::', s.title
                print '|SNIPPET_DESCRIPTION::', s.description
                print '|SNIPPET_LINK::', s.link
                print '|SNIPPET:ESA SCORE::', str(s.filter_status.semantic)
                print '---------------------------------'
            print '>>>>>>>>>>>> ' + str(len(snippets_list)) + ' snippets <<<<<<<<<<'


    def _clean_xml(self, line):
        line2 = re.subn('"', '&quot;', line)
        line3 = re.subn('&', '&amp;', line2[0])
        line4 = re.subn("'", '&apos;', line3[0])
        line5 = re.subn('<', '&lt;', line4[0])
        line6 = re.subn('>', '&gt;', line5[0])
        return line6[0]            

    def _create_person_file(self, id, name):
        file_name = self._output_path + '/' + name + '.' + id + '.xml'
        file_name=re.subn(' ','_',file_name)
        xml_file = open(file_name[0], 'w')
        print >>xml_file, '<?xml version="1.0"?>'
        self.file_name = file_name[0]
        return xml_file
        
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


