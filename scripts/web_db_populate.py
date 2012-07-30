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
# usage: python web_db_populate results_path csv_input_name [True|False|All] ['users'] ['description']

SNIPPET_DESCRIPTION_LENGTH = 500
SNIPPET_LINK_LENGTH = 400
import sys, datetime, os, re, logging, ConfigParser
from lxml import etree

logging.basicConfig(level=logging.INFO)
config = ConfigParser.ConfigParser()
config.read("unoporuno.conf")
if len(config.sections())==0:
    config.read(os.environ['HOME']+"/.unoporuno/unoporuno.conf")
    if len(config.sections())==0:
        logging.error("No configuration file on unoporuno.conf")
        exit(-1)
UNOPORUNO_ROOT = config.get('unoporuno', 'root')
CIDESAL_WEBAPP_PATH = UNOPORUNO_ROOT +'/webapp/'
if not CIDESAL_WEBAPP_PATH in sys.path:
    sys.path.append(CIDESAL_WEBAPP_PATH)
    sys.path.append(CIDESAL_WEBAPP_PATH+'cidesal/')

from unoporuno.models import Busqueda, Persona, Snippet


def main():
    filter_value = None
    colombia = Busqueda()
    colombia.nombre = sys.argv[2]
    results_path = sys.argv[1]
    colombia.fecha = datetime.datetime.now()
    colombia.usuario = '*'
    logging.debug('arguments path:' +sys.argv[1]+  ' name: ' + sys.argv[2])
    if len(sys.argv) > 3:
        filter_value = sys.argv[3]
        logging.debug(' filter_value' +filter_value)
    if len(sys.argv) > 4:
        colombia.usuario = sys.argv[4]
        logging.debug('arguments user:'+sys.argv[4])
    if len(sys.argv) > 5:
        colombia.descripcion = sys.argv[5]
        logging.debug('arguments desc:'+sys.argv[5])
    results_path += '/results_converging/'
    if os.access(results_path, os.R_OK):
        colombia.save()
    else:
        logging.error('No access to '+results_path)
        exit(-1)

    for subdirs, dirs, files in os.walk(results_path):
        for file in files:
            re_xml = re.search('\.xml$', file)
            if not re_xml:
                continue
            logging.debug('processing file: ' +file)
            file_path = results_path + file
            person_tree = etree.parse(file_path)
            person = person_tree.getroot()
            x_name = person.find('name')
            x_geo = person.find('places')
            x_orgs = person.find('orgs')
            x_topics = person.find('topics')
            logging.info('processing person: '+x_name.text)
            w_persona = colombia.persona_set.create(name=x_name.text,
                   geo=x_geo.text, orgs=x_orgs.text,
                   topics=x_topics.text)
            converging_pipelines = person.findall('converging_pipelines')
            for pipeline in converging_pipelines:
                n = pipeline.get('number')
                n_converging = int(n) 
                logging.debug('Processing converging pipeline number '+n)
                snippets_root = pipeline.find('snippets')
                snippets = snippets_root.findall('snippet')
                for x_snippet in snippets:
                    x_query = clean_xml(x_snippet.find('query').text)
                    x_title = clean_xml(x_snippet.find('title').text)
                    x_description = clean_xml(x_snippet.find('description').text)[:SNIPPET_DESCRIPTION_LENGTH]
                    x_link = clean_xml(x_snippet.find('link').text)[:SNIPPET_LINK_LENGTH]
                    x_query_type = x_snippet.find('query_type').text
                    logging.debug('processing snippet '+ x_query +'::'+ x_title)
                    logging.debug('snippet description::' +x_description)
                    logging.debug('snippet link::' +x_link)
                    logging.debug('snippet query_type::' +x_query_type)
                    x_filters = x_snippet.find('filters')
                    x_FG = x_filters.get('FG')
                    x_ESA = x_filters.get('ESA')
                    x_RE = x_filters.get('RE')
                    if x_FG == 'True':
                        b_FG = True
                    else:
                        b_FG = False
                    if x_RE == 'True':
                        b_RE = True
                    else:
                        b_RE = False
                    logging.debug('filters :: FG=' +x_FG+ ' ESA=' +x_ESA+ ' RE=' +x_RE)
                    try:
                        w_snippet = w_persona.snippet_set.create(query=x_query, title=x_title, description=x_description,
                                                 link=x_link, FG=b_FG, RE=b_RE, ESA_score=x_ESA, converging_pipelines=n)
                    except:
                        logging.debug('exception on saving snippet: converting' +w_snippet.description+ \
                                          'of type' +str(type(w_snippet.description)))

                        ascii_title = x_title.encode('ascii', 'replace')
                        ascii_description = x_description.encode('ascii', 'replace')
                        w_snippet = w_persona.snippet_set.create(query=x_query, title=ascii_title, description=ascii_description,
                                                 link=x_link, FG=b_FG, RE=b_RE, ESA_score=x_ESA, converging_pipelines=n)

                    if x_query_type == 'name':
                        w_snippet.name_pipeline = True
                        logging.debug ('filters:: query_type=name')
                    elif x_query_type == 'geo':
                        w_snippet.geo_pipeline = True
                        logging.debug ('filters:: query_type=geo')
                    elif x_query_type == 'orgs':
                        w_snippet.orgs_pipeline = True
                        logging.debug ('filters:: query_type=orgs')
                    elif x_query_type == 'topics':
                        w_snippet.topics_pipeline = True
                        logging.debug ('filters:: query_type=topics')

                    if not filter_value:
                        w_snippet.save()
                    elif filter_value == x_FG:
                        w_snippet.save()
                    elif filter_value == 'All':
                        w_snippet.save()
            colombia.save()
                    
                    

def clean_xml(line):
    if line:
        line2 = re.subn('&quot;', '"', line)
        line3 = re.subn('&amp;', '&', line2[0])
        line4 = re.subn('&apos;', "'", line3[0])
        line5 = re.subn('&lt;', '<', line4[0])
        line6 = re.subn('&gt;', '>', line5[0])
        line_unicode = line6[0]
        return line_unicode
    else:
        return ''
                
            
    
    
    

if __name__ == "__main__":
    main()


