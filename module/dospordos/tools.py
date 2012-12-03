#/usr/bin/env python
# -*- coding: utf8 -*-
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
#
# Generic tools for unoporuno system

__author__="Jorge García Flores"
__date__ ="$08-oct-2011 10:05:30$"

import sys, re, os, logging, nltk

class Limpieza(object):
    def __init__(self):
        #TODO: support propper UTF-8 with NLTK!!!
        self._re_a=re.compile(u'[áâàäãą]')
        self._re_e=re.compile(u'[éèêëěę]')
        self._re_i=re.compile(u'[íïîìı]')
        self._re_o=re.compile(u'[óòôöøōő]')
        self._re_u=re.compile(u'[úùüû]')
        self._re_n=re.compile(u'[ñ]')
        self._re_c=re.compile(u'[ç]')
        self._re_l=re.compile(u'[ł]')
        self._re_s=re.compile(u'[şš]')
        self._re_t=re.compile(u'[ţ]')
        self._re_y=re.compile(u'[ỳýÿŷÿ]')
        self._re_beta=re.compile(u'[ß]')
        self._re_A=re.compile(u'[ÁÀÄÂÅ]')
        self._re_E=re.compile(u'[ÉÈÊË]')
        self._re_I=re.compile(u'[ÍÌÏÎİ]')
        self._re_O=re.compile(u'[ÓÒÔÖØŌ]')
        self._re_U=re.compile(u'[ÚÙÛÜ]')
        self._re_N=re.compile(u'[Ñ]')
        self._re_C=re.compile(u'[Ç]')
        self._re_S=re.compile(u'[ŠŚŞ]]')

        
    def limpia_acentos(self, linea):
        
        linea_u = unicode(linea, 'utf-8', errors='replace')
        
        linea_u = self._re_a.subn('a',linea_u)[0]
        linea_u = self._re_e.subn('e',linea_u)[0]
        linea_u = self._re_i.subn('i',linea_u)[0]
        linea_u = self._re_o.subn('o',linea_u)[0]
        linea_u = self._re_u.subn('u',linea_u)[0]
        linea_u = self._re_n.subn('n',linea_u)[0]
        linea_u = self._re_c.subn('c',linea_u)[0]
        linea_u = self._re_l.subn('l',linea_u)[0]
        linea_u = self._re_s.subn('s',linea_u)[0]
        linea_u = self._re_t.subn('t',linea_u)[0]
        linea_u = self._re_y.subn('y',linea_u)[0]
        linea_u = self._re_beta.subn('ss',linea_u)[0]
        linea_u = self._re_A.subn('A',linea_u)[0]
        linea_u = self._re_E.subn('E',linea_u)[0]
        linea_u = self._re_I.subn('I',linea_u)[0]
        linea_u = self._re_O.subn('O',linea_u)[0]
        linea_u = self._re_U.subn('U',linea_u)[0]
        linea_u = self._re_N.subn('N',linea_u)[0]
        linea_u = self._re_C.subn('C',linea_u)[0]
        linea_u = self._re_S.subn('S',linea_u)[0]
        
        linea_a = linea_u.encode('ascii', 'ignore')
        return linea_a

    def limpia_acentos_latin1(self, linea):
        
        linea_u = unicode(linea, 'latin-1', errors='replace')
        
        linea_u = self._re_a.subn('a',linea_u)[0]
        linea_u = self._re_e.subn('e',linea_u)[0]
        linea_u = self._re_i.subn('i',linea_u)[0]
        linea_u = self._re_o.subn('o',linea_u)[0]
        linea_u = self._re_u.subn('u',linea_u)[0]
        linea_u = self._re_n.subn('n',linea_u)[0]
        linea_u = self._re_c.subn('c',linea_u)[0]
        linea_u = self._re_l.subn('l',linea_u)[0]
        linea_u = self._re_s.subn('s',linea_u)[0]
        linea_u = self._re_t.subn('t',linea_u)[0]
        linea_u = self._re_y.subn('y',linea_u)[0]
        linea_u = self._re_beta.subn('ss',linea_u)[0]
        linea_u = self._re_A.subn('A',linea_u)[0]
        linea_u = self._re_E.subn('E',linea_u)[0]
        linea_u = self._re_I.subn('I',linea_u)[0]
        linea_u = self._re_O.subn('O',linea_u)[0]
        linea_u = self._re_U.subn('U',linea_u)[0]
        linea_u = self._re_N.subn('N',linea_u)[0]
        linea_u = self._re_C.subn('C',linea_u)[0]
        linea_u = self._re_S.subn('S',linea_u)[0]
        
        linea_a = linea_u.encode('ascii', 'ignore')
        return linea_a



    def limpia_reservados_xml(self, linea):
        if linea:
            r = linea.replace('&apos;',"'")
            r = r.replace('&lt;',"<")
            r = r.replace('&gt;',">")
            r = r.replace('&quot;','"')
            r = r.replace('&amp;',"&")
            return r
        else:
            return ''

    def limpia_reservados_regex(self, linea):
        if linea:
            r = linea.replace('.',"\.")
            r = linea.replace('^',"\^")
            r = linea.replace('$',"\$")
            r = linea.replace('*',"\*")
            r = linea.replace('+',"\+")
            r = linea.replace('?',"\?")
            r = linea.replace('{',"\{")
            r = linea.replace('}',"\}")
            r = linea.replace('[',"\[")
            r = linea.replace(']',"\]")
            r = linea.replace('|',"\|")
            r = linea.replace('(',"\(")
            r = linea.replace(')',"\)")
            r = linea.replace('\\',"\\")
            return r
        else:
            return ''


class DiasporaOutput(object):
    def __init__(self, output_path):
        self._output_path = output_path + '/'
        self._xml_buffer = ''
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        self.file_name = ''
        self.limpieza = Limpieza()
        logging.basicConfig(level=logging.INFO)
        

    def open_person(self, persona):
        self._xml_file = self._create_person_file(persona.id, persona.nombre)
        print >> self._xml_file, '\t<person id="' +self._clean_xml(persona.id) + '">'
        print >> self._xml_file, '\t<name>' +self._clean_xml(persona.nombre)+ '</name>'
        print >> self._xml_file, '\t<topics>' +self._clean_xml(persona.temas)+ '</topics>'
        print >> self._xml_file, '\t<orgs>' +self._clean_xml(persona.orgs)+ '</orgs>'
        print >> self._xml_file, '\t<places>' +self._clean_xml(persona.lugares)+ '</places>'
        print >> self._xml_file, '\t<link>' +self._clean_xml(persona.vinculo)+ '</link>'


    def export_unoporuno_busqueda(self, busqueda):
        self._xml_file = self._create_person_file(str(busqueda.id), busqueda.nombre.encode('utf-8'))
        print >> self._xml_file, '<busqueda id="' +str(busqueda.id)+'">'
        print >> self._xml_file, '\t<nombre>' +self._clean_xml(busqueda.nombre.encode('utf-8'))+ '</nombre>'
        print >> self._xml_file, '\t<fecha>' +self._clean_xml(str(busqueda.fecha))+ '</fecha>'
        print >> self._xml_file, '\t<usuario>' +self._clean_xml(busqueda.usuario.encode('utf-8'))+ '</usuario>'
        print >> self._xml_file, '\t<descripcion>' +self._clean_xml(busqueda.descripcion.encode('utf-8'))+ '</descripcion>'
        print >> self._xml_file, '\t<personas>' 
        logging.info('Processing busqueda ' +busqueda.nombre.encode('utf-8'))
        
        for persona in busqueda.persona_set.all():
            logging.info('Exporting person ' +persona.name.encode('utf-8'))
            print >> self._xml_file, '\t\t<person id="' +str(persona.id) + '">'
            print >> self._xml_file, '\t\t<name>' +self._clean_xml(persona.name.encode('utf-8'))+ '</name>'
            print >> self._xml_file, '\t\t<geo>' +self._clean_xml(persona.geo.encode('utf-8'))+ '</geo>'
            print >> self._xml_file, '\t\t<orgs>' +self._clean_xml(persona.orgs.encode('utf-8'))+ '</orgs>'
            print >> self._xml_file, '\t\t<topics>' +self._clean_xml(persona.topics.encode('utf-8'))+ '</topics>'
            print >> self._xml_file, '\t\t<link>' +self._clean_xml(persona.link.encode('utf-8'))+ '</link>'
            print >> self._xml_file, '\t\t<mobility_status>' +str(persona.mobility_status)+ '</mobility_status>'
            print >> self._xml_file, '\t\t<prediction>' +str(persona.prediction)+ '</prediction>'

            print >> self._xml_file, '\t\t<snippets>' 
            for snippet in persona.snippet_set.all():
                print >> self._xml_file,'\t\t<snippet id="' +str(snippet.id)+ '">'
                print >> self._xml_file,'\t\t\t<query>' +self._clean_xml(snippet.query.encode('utf-8'))+ '</query>'
                print >> self._xml_file, '\t\t\t<title>' +self._clean_xml(snippet.title.encode('utf-8'))+ '</title>'
                print >> self._xml_file, '\t\t\t<description>' +self._clean_xml(snippet.description.encode('utf-8'))+ '</description>'
                print >> self._xml_file, '\t\t\t<link>' +self._clean_xml(snippet.link.encode('utf-8'))+ '</link>'
                print >> self._xml_file, '\t\t\t<FG>' +str(snippet.FG)+ '</FG>'
                print >> self._xml_file, '\t\t\t<RE>' +str(snippet.RE)+ '</RE>'
                print >> self._xml_file, '\t\t\t<RE_score>' +str(snippet.RE_score)+ '</RE_score>'
                print >> self._xml_file, '\t\t\t<RE_features>' +str(snippet.RE_features)+ '</RE_features>'                
                print >> self._xml_file, '\t\t\t<ESA_score>' +str(snippet.ESA_score)+ '</ESA_score>'
                print >> self._xml_file, '\t\t\t<converging_pipelines>' +str(snippet.converging_pipelines)+ '</converging_pipelines>'
                print >> self._xml_file, '\t\t\t<name_pipeline>' +str(snippet.name_pipeline)+ '</name_pipeline>'
                print >> self._xml_file, '\t\t\t<geo_pipeline>' +str(snippet.geo_pipeline)+ '</geo_pipeline>'
                print >> self._xml_file, '\t\t\t<orgs_pipeline>' +str(snippet.orgs_pipeline)+ '</orgs_pipeline>'
                print >> self._xml_file, '\t\t\t<topics_pipeline>' +str(snippet.topics_pipeline)+ '</topics_pipeline>'
                print >> self._xml_file, '\t\t\t<pertinente>' +str(snippet.pertinente)+ '</pertinente>'
                print >> self._xml_file, '\t\t\t<evidence_type>' +str(snippet.evidence_type)+ '</evidence_type>'                
                print >> self._xml_file, '\t\t</snippet>'
            print >> self._xml_file, '\t\t</snippets>'

            print >> self._xml_file, '\t\t<vinculos>'
            for vinculo in persona.vinculo_set.all():
                print >> self._xml_file,'\t\t<vinculo id="' +str(vinculo.id)+ '">'
                print >> self._xml_file,'\t\t\t<nombres>'+self._clean_xml(str(vinculo.nombres))+ '</nombres>'
                print >> self._xml_file,'\t\t\t<lugares>'+self._clean_xml(str(vinculo.lugares))+ '</lugares>'
                print >> self._xml_file,'\t\t\t<orgs>'+self._clean_xml(str(vinculo.organizaciones))+ '</orgs>'
                print >> self._xml_file,'\t\t\t<desc>' +self._clean_xml(vinculo.descripcion.encode('utf-8'))+ '</desc>'
                print >> self._xml_file,'\t\t\t<tipo>'+str(vinculo.tipo)+ '</tipo>'
                print >> self._xml_file,'\t\t</vinculo>'
            print >> self._xml_file, '\t\t</vinculos>'
            
            print >> self._xml_file, '\t\t</person>'

        print >> self._xml_file, '\t</personas>' 
        print >> self._xml_file, '</busqueda>'        
        self._xml_file.close()

    def export_unoporuno_persona(self, busqueda, id_list):
        self._xml_file = self._create_person_file(str(busqueda.id), busqueda.nombre.encode('utf-8'))
        print >> self._xml_file, '<busqueda id="' +str(busqueda.id)+'">'
        print >> self._xml_file, '\t<nombre>' +self._clean_xml(busqueda.nombre.encode('utf-8'))+ '</nombre>'
        print >> self._xml_file, '\t<fecha>' +self._clean_xml(str(busqueda.fecha))+ '</fecha>'
        print >> self._xml_file, '\t<usuario>' +self._clean_xml(busqueda.usuario.encode('utf-8'))+ '</usuario>'
        print >> self._xml_file, '\t<descripcion>' +self._clean_xml(busqueda.descripcion.encode('utf-8'))+ '</descripcion>'
        print >> self._xml_file, '\t<personas>'
        logging.info('Processing busqueda ' +busqueda.nombre.encode('utf-8'))
        logging.debug('Person id list=' +str(id_list))
        
        for persona in busqueda.persona_set.all():
            if str(persona.id) not in id_list:
                continue
            logging.info('Exporting person ' +persona.name.encode('utf-8')+ ' with id=' +str(persona.id))
            print >> self._xml_file, '\t\t<person id="' +str(persona.id) + '">'
            print >> self._xml_file, '\t\t<name>' +self._clean_xml(persona.name.encode('utf-8'))+ '</name>'
            print >> self._xml_file, '\t\t<geo>' +self._clean_xml(persona.geo.encode('utf-8'))+ '</geo>'
            print >> self._xml_file, '\t\t<orgs>' +self._clean_xml(persona.orgs.encode('utf-8'))+ '</orgs>'
            print >> self._xml_file, '\t\t<topics>' +self._clean_xml(persona.topics.encode('utf-8'))+ '</topics>'
            print >> self._xml_file, '\t\t<link>' +self._clean_xml(persona.link.encode('utf-8'))+ '</link>'
            print >> self._xml_file, '\t\t<snippets>' 

            for snippet in persona.snippet_set.all():
                print >> self._xml_file,'\t\t<snippet id="' +str(snippet.id)+ '">'
                print >> self._xml_file,'\t\t\t<query>' +self._clean_xml(snippet.query.encode('utf-8'))+ '</query>'
                print >> self._xml_file, '\t\t\t<title>' +self._clean_xml(snippet.title.encode('utf-8'))+ '</title>'
                print >> self._xml_file, '\t\t\t<description>' +self._clean_xml(snippet.description.encode('utf-8'))+ '</description>'
                print >> self._xml_file, '\t\t\t<link>' +self._clean_xml(snippet.link.encode('utf-8'))+ '</link>'
                print >> self._xml_file, '\t\t\t<FG>' +str(snippet.FG)+ '</FG>'
                print >> self._xml_file, '\t\t\t<RE>' +str(snippet.RE)+ '</RE>'
                print >> self._xml_file, '\t\t\t<RE_score>' +str(snippet.RE_score)+ '</RE_score>'
                print >> self._xml_file, '\t\t\t<RE_features>' +str(snippet.RE_features)+ '</RE_features>'                
                print >> self._xml_file, '\t\t\t<ESA_score>' +str(snippet.ESA_score)+ '</ESA_score>'
                print >> self._xml_file, '\t\t\t<converging_pipelines>' +str(snippet.converging_pipelines)+ '</converging_pipelines>'
                print >> self._xml_file, '\t\t\t<name_pipeline>' +str(snippet.name_pipeline)+ '</name_pipeline>'
                print >> self._xml_file, '\t\t\t<geo_pipeline>' +str(snippet.geo_pipeline)+ '</geo_pipeline>'
                print >> self._xml_file, '\t\t\t<orgs_pipeline>' +str(snippet.orgs_pipeline)+ '</orgs_pipeline>'
                print >> self._xml_file, '\t\t\t<topics_pipeline>' +str(snippet.topics_pipeline)+ '</topics_pipeline>'
                print >> self._xml_file, '\t\t\t<pertinente>' +str(snippet.pertinente)+ '</pertinente>'
                print >> self._xml_file, '\t\t\t<evidence_type>' +str(snippet.evidence_type)+ '</evidence_type>'                
                print >> self._xml_file, '\t\t</snippet>'

            print >> self._xml_file, '\t\t</snippets>'
            print >> self._xml_file, '\t\t</person>'

        print >> self._xml_file, '\t</personas>' 
        print >> self._xml_file, '</busqueda>'        
        self._xml_file.close()



    def open_unoporuno_person(self, persona):
        self._xml_file = self._create_person_file(str(persona.id), persona.name.encode('utf-8'))
        

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


    def write_unorporuno_snippets(self, snippets_list, converging_number):
        #TODO: copiar todos y cada uno de los campos de la base de datos
        print >> self._xml_file, '<converging_pipelines number="' +str(converging_number)+ '">'
        print >> self._xml_file, '\t<stats>'
        print >> self._xml_file, '\t\t<total_snippets>' +str(len(snippet_list))+ '</total_snippets>'
        print >> self._xml_file, '\t\t<link_found></link_found>'
        print >> self._xml_file, '\t</stats>'
        print >> self._xml_file, '\t<snippets>'
        logging.debug('PipelineStatus:: ps.snippets.type='+str(type(snippets_list)))
        logging.debug('PipelineStatus:: ps.snippets.len='+str(len(snippets_list)))
        for s in snippets_list:
            logging.debug('PipelineStatus:: adding to xml:' +s.title.encode('utf-8'))
            print >> self._xml_file, '\t\t<snippet>'
            print >> self._xml_file, '\t\t<query>' +self._clean_xml(s.query.encode('utf-8'))+ '</query>'
            print >> self._xml_file, '\t\t\t<title>' +self._clean_xml(s.title.encode('utf-8'))+ '</title>'
            status = s.filter_status.vinculo_encontrado
            print >> self._xml_file, '\t\t\t<description>' +self._clean_xml(s.description.encode('utf-8'))+ '</description>'
            print >> self._xml_file, '\t\t\t<link status="' +str(s.pertinente)+ '">' +self._clean_xml(s.link.encode('utf-8'))+ '</link>'
            print >> self._xml_file, '\t\t\t<query_type>' +s.query_type+ '</query_type>'

            
            FG = s.filter_status.nominal
            ESA = s.filter_status.semantic
            RE = s.filter_status.biographic
            print >> self._xml_file, '\t\t<filters FG="' +str(FG)+ '" ESA="' +str(ESA)+ '" RE="' +str(RE)+ '"/>'
            print >> self._xml_file, '\t\t</snippet>'
        print >> self._xml_file, '\t</snippets>'
        print >> self._xml_file, '</converging_pipelines>'    

    def write_to_db(self, write_type, nombre, arg_db_busqueda=None, filter='All', user='', description=''):
        logging.debug('writing person file_name = ' +self.file_name+ ' to database')
        if not arg_db_busqueda:
            db_busqueda = Busqueda_DB(UNOPORUNO_ROOT)
        else:
            db_busqueda = arg_db_busqueda
        busqueda_id = 0
        if write_type == 'new':    
            busqueda_id = db_busqueda.new(nombre, filter, user, description)
            db_busqueda.update_person_from_file(self.file_name)
        elif write_type == 'update':
            db_busqueda.get(nombre, filter)
            db_busqueda.update_person_from_file(self.file_name)
        return busqueda_id

    def write_to_db(self, write_type, nombre, filter='All', user='', description=''):
        logging.debug('writing person file_name = ' +self.file_name+ ' to database')
        db_busqueda = Busqueda_DB(UNOPORUNO_ROOT)
        busqueda_id = 0
        if write_type == 'new':
            busqueda_id = db_busqueda.new(nombre, filter, user, description)
            db_busqueda.update_person_from_file(self.file_name)
        elif write_type == 'update':
            db_busqueda.get(nombre, filter)
            db_busqueda.update_person_from_file(self.file_name)
        return busqueda_id

    
    def write_person_to_db(self, write_type, nombre,db_busqueda, filter='All', user='', description=''):
         logging.debug('writing person file_name = ' +self.file_name+ ' to database')
         person_id = 0
         if write_type == 'update':
             db_busqueda.get(nombre, filter)
             person_id = db_busqueda.update_person_from_file(self.file_name)
         return person_id



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

    def write_personal_feature_matrix_2class(self, persona):
        heading = """
@attribute ID string
@attribute tesis {0,1}
@attribute linkedin {0,1}
@attribute publication {0,1}
@attribute email {0,1}
@attribute world_nat {0,1}
@attribute latin_nat {0,1}
@attribute name_in_http {0,1}
@attribute cv {0,1}
@attribute degree {0,1}
@attribute prof {0,1}
@attribute bio {0,1}
@attribute accro {0,1}
@attribute city {0,1}
@attribute country {0,1}
@attribute org {0,1}
@attribute class {0,1}

@data
        """
        file_name = self._output_path + '/' + str(persona.id) + '.1x1.arff'
        person_file = open(file_name, 'w')
        heading = '@relation ' + str(persona.id) + '.1x1.arff\n' + heading
        print >> person_file, heading
        for s in persona.snippet_set.filter(FG=1).exclude(RE=1):
             if s.evidence_type is None:
                 evidence_type = '0'
             elif s.evidence_type >= 2:
                 evidence_type = '0'
             else:
                 evidence_type = str(s.evidence_type)
             if s.RE_features is None:
                 RE_features = '0'
             else:
                 RE_features = str(bin(int(s.RE_features))).replace('0b','')
             features = str(RE_features.zfill(15))
             features_str = ''
             for c in features:
                 features_str += c+','
             print_str = str(s.id) + ',' + features_str + str(evidence_type)
             print >> person_file, print_str
        return file_name


    def write_personal_feature_matrix_2class_fc(self, persona):
        heading = """
@attribute ID string
@attribute tesis {0,1}
@attribute linkedin {0,1}
@attribute publication {0,1}
@attribute email {0,1}
@attribute world_nat {0,1}
@attribute latin_nat {0,1}
@attribute name_in_http {0,1}
@attribute cv {0,1}
@attribute degree {0,1}
@attribute prof {0,1}
@attribute bio {0,1}
@attribute accro {0,1}
@attribute city {0,1}
@attribute country {0,1}
@attribute org {0,1}
@attribute feature_count {0,1,2,3,4,5,6,7,8,9}
@attribute class {0,1}

@data
        """
        file_name = self._output_path + '/' + str(persona.id) + '.1x1.arff'
        person_file = open(file_name, 'w')
        heading = '@relation ' + str(persona.id) + '.1x1.arff\n' + heading
        print >> person_file, heading
        for s in persona.snippet_set.filter(FG=1).exclude(RE=1):
             if s.evidence_type is None:
                 evidence_type = '0'
             elif s.evidence_type >= 2:
                 evidence_type = '0'
             else:
                 evidence_type = str(s.evidence_type)
             if s.RE_features is None:
                 RE_features = '0'
             else:
                 RE_features = str(bin(int(s.RE_features))).replace('0b','')
             features = str(RE_features.zfill(15))
             features_str = ''
             feature_count=0
             for c in features:
                 features_str += c+','
                 feature_count += 1 if c=='1' else 0
             print_str = str(s.id) + ',' + features_str + str(feature_count)+ ',' +str(evidence_type)
             print >> person_file, print_str
        return file_name

    
    def write_personal_feature_matrix_3class(self, persona):
        heading = """
@attribute ID string
@attribute tesis {0,1}
@attribute linkedin {0,1}
@attribute publication {0,1}
@attribute email {0,1}
@attribute world_nat {0,1}
@attribute latin_nat {0,1}
@attribute name_in_http {0,1}
@attribute cv {0,1}
@attribute degree {0,1}
@attribute prof {0,1}
@attribute bio {0,1}
@attribute accro {0,1}
@attribute city {0,1}
@attribute country {0,1}
@attribute org {0,1}
@attribute feature_count {0,1,2,3,4,5,6,7,8,9}
@attribute class {0,1,2}

@data
        """
        file_name = self._output_path + '/' + str(persona.id) + '.1x1.arff'
        person_file = open(file_name, 'w')
        heading = '@relation ' + str(persona.id) + '.1x1.arff\n' + heading
        print >> person_file, heading
        for s in persona.snippet_set.filter(FG=1).exclude(RE=1):
             if s.evidence_type is None:
                 evidence_type = '0'
             elif s.evidence_type in (0,1,2):
                 evidence_type = str(s.evidence_type)
             elif s.evidence_type > 2:
                 evidence_type = '2'
             if s.RE_features is None:
                 RE_features = '0'
             else:
                 RE_features = str(bin(int(s.RE_features))).replace('0b','')
             features = str(RE_features.zfill(15))
             features_str = ''
             feature_count=0
             for c in features:
                 features_str += c+','
                 feature_count += 1 if c=='1' else 0
             print_str = str(s.id) + ',' + features_str + str(feature_count)+ ',' +str(evidence_type)
             print >> person_file, print_str
        return file_name

    def write_busqueda_feature_matrix_2class(self, busqueda):
    #WARNING: converging_pipelines >> 5
        heading = """
@attribute ID string
@attribute tesis {0,1}
@attribute linkedin {0,1}
@attribute publication {0,1}
@attribute email {0,1}
@attribute world_nat {0,1}
@attribute latin_nat {0,1}
@attribute name_in_http {0,1}
@attribute cv {0,1}
@attribute degree {0,1}
@attribute prof {0,1}
@attribute bio {0,1}
@attribute accro {0,1}
@attribute city {0,1}
@attribute country {0,1}
@attribute org {0,1}
@attribute class {0,1}

@data
        """
        file_name = self._output_path + '/' + str(busqueda.id) + '.1x1.arff'
        person_file = open(file_name, 'w')
        heading = '@relation ' + file_name + '\n' + heading
        print >> person_file, heading
        for persona in busqueda.persona_set.all():
            for s in persona.snippet_set.filter(FG=1).exclude(RE=1):
                 if s.evidence_type is None:
                     evidence_type = '0'
                 elif s.evidence_type >=2:
                     evidence_type = '0'
                 else:
                     evidence_type = str(s.evidence_type)
                 if s.RE_features is None:
                     RE_features = '0'
                 else:
                     RE_features = str(bin(int(s.RE_features))).replace('0b','')
                 features = str(RE_features.zfill(15))
                 features_str = ''
                 for c in features:                     
                     features_str += c+','
                 print_str = str(s.id) + ',' + features_str + str(evidence_type)
                 print >> person_file, print_str
        return file_name

    def write_busqueda_feature_matrix_3class(self, busqueda):
    #WARNING: converging_pipelines >> 5
    #with feature count
        heading = """
@attribute ID string
@attribute tesis {0,1}
@attribute linkedin {0,1}
@attribute publication {0,1}
@attribute email {0,1}
@attribute world_nat {0,1}
@attribute latin_nat {0,1}
@attribute name_in_http {0,1}
@attribute cv {0,1}
@attribute degree {0,1}
@attribute prof {0,1}
@attribute bio {0,1}
@attribute accro {0,1}
@attribute city {0,1}
@attribute country {0,1}
@attribute org {0,1}
@attribute feature_count {0,1,2,3,4,5,6,7,8,9}
@attribute class {0,1,2}

@data
        """
        file_name = self._output_path + '/' + str(busqueda.id) + '.1x1.arff'
        person_file = open(file_name, 'w')
        heading = '@relation ' + file_name + '\n' + heading
        print >> person_file, heading
        for persona in busqueda.persona_set.all():
            for s in persona.snippet_set.filter(FG=1).exclude(RE=1):
                 if s.evidence_type is None:
                     evidence_type = '0'
                 elif s.evidence_type in (0,1,2):
                     evidence_type = str(s.evidence_type)
                 elif s.evidence_type > 2:
                     evidence_type = '2'
                 if s.RE_features is None:
                     RE_features = '0'
                 else:
                     RE_features = str(bin(int(s.RE_features))).replace('0b','')                     
                 features = str(RE_features.zfill(15))
                 features_str = ''
                 feature_count = 0
                 for c in features:
                     features_str += c+','
                     feature_count +=1 if c=='1' else 0
                 print_str = str(s.id) + ',' + features_str + str(feature_count) + ',' + str(evidence_type)
                 print >> person_file, print_str
        return file_name


    def write_busqueda_feature_matrix_2class_fc(self, busqueda):
    #WARNING: converging_pipelines >> 5
    #with feature count
        heading = """
@attribute ID string
@attribute tesis {0,1}
@attribute linkedin {0,1}
@attribute publication {0,1}
@attribute email {0,1}
@attribute world_nat {0,1}
@attribute latin_nat {0,1}
@attribute name_in_http {0,1}
@attribute cv {0,1}
@attribute degree {0,1}
@attribute prof {0,1}
@attribute bio {0,1}
@attribute accro {0,1}
@attribute city {0,1}
@attribute country {0,1}
@attribute org {0,1}
@attribute feature_count {0,1,2,3,4,5,6,7,8,9}
@attribute class {0,1}

@data
        """
        file_name = self._output_path + '/' + str(busqueda.id) + '.1x1.arff'
        person_file = open(file_name, 'w')
        heading = '@relation ' + file_name + '\n' + heading
        print >> person_file, heading
        for persona in busqueda.persona_set.all():
            for s in persona.snippet_set.filter(FG=1).exclude(RE=1):
                 if s.evidence_type is None:
                     evidence_type = '0'
                 elif s.evidence_type in (0,1):
                     evidence_type = str(s.evidence_type)
                 elif s.evidence_type > 1:
                     evidence_type = '0'
                 if s.RE_features is None:
                     RE_features = '0'
                 else:
                     RE_features = str(bin(int(s.RE_features))).replace('0b','')                     
                 features = str(RE_features.zfill(15))
                 features_str = ''
                 feature_count = 0
                 for c in features:
                     features_str += c+','
                     feature_count +=1 if c=='1' else 0
                 print_str = str(s.id) + ',' + features_str + str(feature_count) + ',' + str(evidence_type)
                 print >> person_file, print_str
        return file_name


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


class DetectaLengua(object):
#TODO: crap lexical detection... make up something niche with HMM or Naive Bayes
    def __init__(self, esp_vocab_file=''):
        logging.basicConfig(level=logging.DEBUG)
        self.__limpia = Limpieza()
        self.__retokens=re.compile(u'[ \.;,_?!\-]')
        #todo optimizar para que sólo transforme aquellas que no sean isalpha, es decir que tengan acento
        
        self.english_vocab = set(w.lower() for w in nltk.corpus.words.words())
        self.spanish_vocab = set()
        try:
            logging.debug('trying to open ' +esp_vocab_file)
            esp_vocab = open(esp_vocab_file, 'r')
            for v in esp_vocab:
                self.spanish_vocab.add(v.strip())
        except:
            logging.debug('slowly building spanish vocab')
            for w in nltk.corpus.cess_esp.words():
                if w.isalpha():
                    self.spanish_vocab.add(w.lower())
                else:
                    w_no_accents = self.__limpia.limpia_acentos_latin1(w)
                    if w_no_accents.isalpha():
                        self.spanish_vocab.add(w_no_accents.lower())
        
                
    def lengua(self, test):
        
        test_na = self.__limpia.limpia_acentos(test)
        test_list = self.__retokens.split(test_na)
        logging.debug('test_list=' +str(test_list))
        test_vocab = set(w.lower() for w in test_list if w.isalpha())
        unusual_eng = test_vocab.difference(self.english_vocab)
        unusual_esp = test_vocab.difference(self.spanish_vocab)
        if unusual_eng > unusual_esp:
            return 'esp'
        elif unusual_esp > unusual_eng:
            return 'eng'
        else:
            return 'unknown'
        

        
        
