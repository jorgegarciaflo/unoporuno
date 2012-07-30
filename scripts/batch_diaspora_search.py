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
# usage: python batch_diaspora_search.py input_file.xml output_file.xml
#        input_file.xml = persons to search
#        output_file.xml = search results


from unoporuno.buscador import BuscadorDiasporas, ErrorBuscador
import sys, time, logging, re

COLUMN_SEPARATOR = '|'
ROW_SIZE = 6
TOPIC_SEPARATOR = ';'

def main():
    logging.basicConfig(level=logging.DEBUG)
    personas_file = PersonasInput()
    personas_file.open_csv(sys.argv[1])
    personas = personas_file.read()
    buscador = BuscadorDiasporas()
    diaspora_output = DiasporaOutput(sys.argv[2])
    for p in personas:
        diaspora_output.open_person(p)
        logging.info ('batch_diaspora_search::processing '+ p.nombre)
        r = reloj()
        buscador.inicia(p.nombre, p.vinculo)
        #********
        # PIPELINE name
        #********
        resultado_busqueda = buscador.genera_busquedas_nominales()  
        resultado_busqueda.filtra_nominal(p.nombre)
        r.stop()
        #******** FILTRO
        #********        NOMINAL
        ps = PipelineStats()
        ps.type = 'name'
        ps.total_queries = resultado_busqueda.total_queries
        ps.total_snippets = len(resultado_busqueda.snippets)
        ps.tiempo_proceso = r.tiempo()[0]
        ps.encontro_vinculo = resultado_busqueda.vinculo_encontrado
        diaspora_output.write_pipeline(ps, list(resultado_busqueda.snippets))
        if ps.encontro_vinculo:
            diaspora_output.close_person()
            continue
        #********
        # PIPELINE geo
        #********
        resultado_busqueda = buscador.genera_busquedas_geograficas(p.lugares)
        resultado_busqueda.filtra_nominal(p.nombre)
        r.stop()
        ps = PipelineStats()
        ps.type = 'geo'
        ps.total_queries = resultado_busqueda.total_queries
        ps.total_snippets = len(resultado_busqueda.snippets)
        ps.tiempo_proceso = r.tiempo()[0]
        ps.encontro_vinculo = resultado_busqueda.vinculo_encontrado
        diaspora_output.write_pipeline(ps, list(resultado_busqueda.snippets))
        if ps.encontro_vinculo:
            diaspora_output.close_person()
            continue

        #********
        # PIPELINE topics 
        #********
        resultado_busqueda = buscador.genera_busquedas_tematicas(p.temas)
        resultado_busqueda.filtra_nominal(p.nombre)
        r.stop()
        ps = PipelineStats()
        ps.type = 'topics'
        ps.total_queries = resultado_busqueda.total_queries
        ps.total_snippets = len(resultado_busqueda.snippets)
        ps.tiempo_proceso = r.tiempo()[0]
        ps.encontro_vinculo = resultado_busqueda.vinculo_encontrado
        diaspora_output.write_pipeline(ps, list(resultado_busqueda.snippets))
        if ps.encontro_vinculo:
            diaspora_output.close_person()
            continue
        

        #********
        # PIPELINE orgs
        #********
        resultado_busqueda = buscador.genera_busquedas_organizacionales(p.orgs)
        resultado_busqueda.filtra_nominal(p.nombre)
        r.stop()
        ps = PipelineStats()
        ps.type = 'orgs'
        ps.total_queries = resultado_busqueda.total_queries
        ps.total_snippets = len(resultado_busqueda.snippets)
        ps.tiempo_proceso = r.tiempo()[0]
        ps.encontro_vinculo = resultado_busqueda.vinculo_encontrado
        diaspora_output.write_pipeline(ps, list(resultado_busqueda.snippets))
        if ps.encontro_vinculo:
            diaspora_output.close_person()
            continue
        diaspora_output.close_person()
        
                
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
            if tamano == ROW_SIZE:  #with link
                p = Persona(columnas[0], columnas[1], columnas[2], \
                            columnas[3], columnas[4], columnas[5])
                personas_list.append(p)
            elif tamano == (ROW_SIZE-1): #without link
                p = Persona(columnas[0], columnas[1], columnas[2], \
                            columnas[3], columnas[4])
                personas_list.append(p)
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
            print >> self._xml_file, '\t\t\t<query>' +self._clean_xml(s.query)+ '</query>'
            print >> self._xml_file, '\t\t\t<title>' +self._clean_xml(s.title)+ '</title>'
            print >> self._xml_file, '\t\t\t<description>' +self._clean_xml(s.title)+ '</description>'
            status = s.filter_status.vinculo_encontrado
            print >> self._xml_file, '\t\t\t<link status="' +str(status)+ '">' +self._clean_xml(s.link)+ '</link>'
            print >> self._xml_file, '\t\t\t<engine>' +self._clean_xml(s.engine)+ '</engine>'
            FG = s.filter_status.nominal
            ESA = s.filter_status.semantic
            RE = s.filter_status.biographic
            print >> self._xml_file, '\t\t\t<filters FG="' +str(FG)+ '" ESA="' +str(ESA)+ '" RE="' +str(RE)+ '"/>'
            print >> self._xml_file, '\t\t</snippet>'
        print >> self._xml_file, '\t</snippets>'
        print >> self._xml_file, '\t</pipeline>' 
        
        
    
    def write_filter(self, filter):
        pass


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
        return xml_file
        
class reloj:
    def __init__(self):
        self._start = time.time()
        self._stop = time.time()

    def stop(self):
        self._stop = time.time()

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



if __name__ == "__main__":
    main()
