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
# TODO: error recording a snippet with unicode characters

# CHANGE LOG
# 17/01/12: cambio en update person from file para truncar los campos x_name, x_topics, x_org, x_geo y x_link de acuerdo a las limitaciones especificadas en
#           UNOPORUNO_ROOT/webapp/cidesal/unoporuno/models.py

SNIPPET_DESCRIPTION_LENGTH = 500
SNIPPET_LINK_LENGTH = 400
import sys, os, re
import datetime, logging, ConfigParser
from lxml import etree

#busca unoporuno.conf en el directorio local, y luego en $HOME/.unoporuno/unoporuno.conf


class Busqueda_DB(object):
    def __init__(self, unoporuno_root):
        logging.basicConfig(level=logging.DEBUG)
        self.unoporuno_root = unoporuno_root
        self.unoporuno_modules = unoporuno_root + "/modules/"
        self.webapp_path = unoporuno_root + "/webapp/"

    def new(self, name, fg_select='All', user='', description=''):
        logging.debug ("busqueda_db::nueva búsqueda")        
        if not self.webapp_path in sys.path:
            sys.path.append(self.webapp_path)
            sys.path.append(self.webapp_path+'cidesal/')
        from unoporuno.models import Busqueda, Persona, Snippet
        
        self.busqueda = Busqueda()
        self.busqueda.nombre = name
        self.busqueda.fecha = datetime.datetime.now()
        self.busqueda.usuario = user
        self.busqueda.descripcion = description
        self.FG_select = fg_select
        self.busqueda.save()
        return int(self.busqueda.id)
        
    def get(self, busqueda_id, fg_select='All'):
        if not self.webapp_path in sys.path:
            sys.path.append(self.webapp_path)
            sys.path.append(self.webapp_path+'cidesal/')
        from unoporuno.models import Busqueda, Persona, Snippet    
        logging.debug ("busqueda_db::leyendo datos de búsqueda " +str(busqueda_id))
        self.busqueda = Busqueda.objects.get(id=busqueda_id)
        self.FG_select = fg_select
        
    def delete(self, busqueda_id, name=''):
        logging.debug ("busqueda_db::deleting busqueda_id:" +str(id))
        if not self.webapp_path in sys.path:
            sys.path.append(self.webapp_path)
            sys.path.append(self.webapp_path+'cidesal/')
        from unoporuno.models import Busqueda, Persona, Snippet
        self.busqueda = Busqueda.objects.get(id=busqueda_id)
        self.busqueda.delete()
    
        
    def update_person_from_file(self, file_path):
        if not os.access(file_path, os.R_OK):
            logging.error('No access to '+file_path)
            return False
        filter_value = self.FG_select
        re_xml = re.search('\.xml$', file_path)
        if not re_xml:
            logging.error(file_path +' is not an xml file')
            return False
        logging.debug('Busqueda_DB::processing file: ' +file_path)
        person_tree = etree.parse(file_path)
        person = person_tree.getroot()
        #change_log 17/01/12 JGF
        # los límites están especificados en 
        # UNOPORUNO_ROOT/webapp/cidesal/unoporuno/models.py
        x_name = person.find('name').text[:250]
        x_geo = person.find('places').text[:300] if person.find('places').text else ''
        x_orgs = person.find('orgs').text[:400] if person.find('orgs').text else ''
        x_topics = person.find('topics').text[:400] if person.find('topics').text else ''
        x_link = person.find('link') if person.find('link').text else ''
        if x_name is None:
            return False
        if x_name is None:
            x_name = ''
        if x_orgs is None:
            x_orgs = ''
        if x_geo is None:
            x_geo = ''
        if x_topics is None:
            x_topics = ''
        if x_link is None:
            x_link = ''
        logging.info('processing person: '+x_name)
        logging.debug('x_geo=' + x_geo +'of type ' +str(type(x_geo)))
        logging.debug('x_orgs=' + x_orgs +'of type ' +str(type(x_orgs)))
        logging.debug('x_topics=' + x_topics +'of type ' +str(type(x_topics)))
        w_persona = self.busqueda.persona_set.create(name=x_name,
               geo=x_geo, orgs=x_orgs,
               topics=x_topics, link=x_link)
        converging_pipelines = person.findall('converging_pipelines')
        for pipeline in converging_pipelines:
            n = pipeline.get('number')
            n_converging = int(n) 
            logging.debug('Busqueda_DB::Processing converging pipeline number '+n)
            snippets_root = pipeline.find('snippets')
            snippets = snippets_root.findall('snippet')
            for x_snippet in snippets:
                x_query = self.clean_xml(x_snippet.find('query').text)
                x_title = self.clean_xml(x_snippet.find('title').text)
                x_description = self.clean_xml(x_snippet.find('description').text)[:SNIPPET_DESCRIPTION_LENGTH]
                x_link = self.clean_xml(x_snippet.find('link').text)[:SNIPPET_LINK_LENGTH]
                x_query_type = x_snippet.find('query_type').text
                logging.debug('Busqueda_DB::processing snippet '+ x_query +'::'+ x_title)
                logging.debug('Busqueda_DB::snippet description::' +x_description)
                logging.debug('Busqueda_DB::snippet link::' +x_link)
                logging.debug('Busqueda_DB::snippet query_type::' +x_query_type)
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
                logging.debug('Busqueda_DB::filters :: FG=' +x_FG+ ' ESA=' +x_ESA+ ' RE=' +x_RE)
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
        self.busqueda.save()
        return w_persona.id                    

    def clean_xml(self, line):
        if line:
            line2 = re.subn('&quot;', '"', line)
            line3 = re.subn('&amp;', '&', line2[0])
            line4 = re.subn('&apos;', "'", line3[0])
            line5 = re.subn('&lt;', '<', line4[0])
            line6 = re.subn('&gt;', '>', line5[0])
            return line6[0]
        else:
            return ''

    


