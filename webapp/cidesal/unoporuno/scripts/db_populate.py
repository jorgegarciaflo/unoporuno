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
# usage: python populate_webapp_db.py data_directory pipeline_type busqueda_id
SNIPPET_DESCRIPTION_LENGTH = 500
SNIPPET_LINK_LENGTH = 400
import sys, datetime, os, re, logging
from lxml import etree
CIDESAL_WEBAPP_PATH='/home/jgflores/cidesal/code/unoporuno/webapp/'
if not CIDESAL_WEBAPP_PATH in sys.path:
    sys.path.append(CIDESAL_WEBAPP_PATH)
    sys.path.append(CIDESAL_WEBAPP_PATH+'cidesal/')

from unoporuno.models import Busqueda, Persona, Snippet


def main():
    logging.basicConfig(level=logging.DEBUG)
    #colombia = Busqueda()
    colombia = Busqueda.objects.get(id=2)
    #colombia.nombre = 'colombia.converging.jun2011'
    #colombia.fecha = datetime.datetime(2011, 6, 17, 0, 0)
    #colombia.usuario = 'Jorge, Bill'
    #colombia.save()
    results_path = '/home/jgflores/cidesal/code/unoporuno/experiences/colombia.converging.jun2011.querytype/results_converging/'
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
                    logging.debug('filters :: FG=' +x_FG+ ' ESA=' +x_ESA+ ' RE=' +x_RE)
                    w_snippet = w_persona.snippet_set.create(query=x_query, title=x_title, description=x_description,
                                                 link=x_link, FG=x_FG, RE=x_RE, ESA_score=x_ESA, converging_pipelines=n)
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
                    w_snippet.save()
            colombia.save()
                    
                    

def clean_xml(line):
    if line:
        line2 = re.subn('&quot;', '"', line)
        line3 = re.subn('&amp;', '&', line2[0])
        line4 = re.subn('&apos;', "'", line3[0])
        line5 = re.subn('&lt;', '<', line4[0])
        line6 = re.subn('&gt;', '>', line5[0])
        return line6[0]
    else:
        return ''
                
            
    
    
    

if __name__ == "__main__":
    main()


