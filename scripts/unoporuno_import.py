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
# usage: python unoporuno_import.py unoporuno_xml_file
# exports a unoporuno database to an xml file following unopourno DTD
#


import logging, ConfigParser, sys
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
UNOPORUNO_PATH = UNOPORUNO_ROOT + '/module/'
CIDESAL_WEBAPP_PATH = UNOPORUNO_ROOT +'/webapp/'

if not CIDESAL_WEBAPP_PATH in sys.path:
    sys.path.append(CIDESAL_WEBAPP_PATH)
    sys.path.append(CIDESAL_WEBAPP_PATH+'cidesal/')
from unoporuno.models import Busqueda, Persona, Snippet

if not UNOPORUNO_PATH in sys.path:
        sys.path.append(UNOPORUNO_PATH)
from dospordos.tools import DiasporaOutput, Limpieza

try:
    xml_file = sys.argv[1]
    busqueda_xml = etree.parse(xml_file)
except:
    logging.error('Invalid file' +xml_file)
    logging.error('Usage: python unoporuno_import xml_file_name')
    exit(-1)

logging.info('Processing file ' +xml_file)
L = Limpieza()
x_busqueda = busqueda_xml.getroot()
x_nombre = x_busqueda.find('nombre')
x_fecha = x_busqueda.find('fecha')
x_usuario = x_busqueda.find('usuario')
x_descripcion = x_busqueda.find('descripcion')
busqueda = Busqueda()
busqueda.nombre = L.limpia_reservados_xml(x_nombre.text)
busqueda.fecha = x_fecha.text
busqueda.usuario = L.limpia_reservados_xml(x_usuario.text)
busqueda.descripcion = L.limpia_reservados_xml(x_descripcion.text)
busqueda.save()
logging.info('Importing busqueda ' +busqueda.nombre)
x_personas = x_busqueda.find('personas')
x_personas_set = x_personas.findall('person')
limpia = L.limpia_reservados_xml
for x_persona in x_personas_set:
    persona = Persona()
    persona.busqueda = busqueda
    persona.name = limpia(x_persona.find('name').text)
    persona.geo = limpia(x_persona.find('geo').text)
    persona.orgs = limpia(x_persona.find('orgs').text)
    persona.topics = limpia(x_persona.find('topics').text)
    persona.link = limpia(x_persona.find('link').text)
    persona.save()
    logging.info('Importing person ' +persona.name)
    x_snippets = x_persona.find('snippets')
    x_snippets_set = x_snippets.findall('snippet')
    for x_snippet in x_snippets_set:
        snippet = Snippet()
        snippet.persona = persona
        snippet.query = limpia(x_snippet.find('query').text)
        snippet.title = limpia(x_snippet.find('title').text)
        snippet.description = limpia(x_snippet.find('description').text)
        snippet.link = limpia(x_snippet.find('link').text)
        logging.debug('processing snippet ' +snippet.link)
        if x_snippet.find('FG').text =='True':
            snippet.FG = True
        else:
            snippet.FG = False
        if x_snippet.find('RE').text == 'True':
            snippet.RE = True
        else:
            snippet.RE = False
        try:
            snippet.RE_score = x_snippet.find('RE_score').text
            snippet.save()
        except:
            snippet.RE_score = None
        try:
            snippet.ESA_score = x_snippet.find('ESA_score').text
            snippet.save()
        except:
            snippet.ESA_score = None
        try:
            snippet.RE_features = x_snippet.find('RE_features').text
            snippet.save()
        except:
            snippet.RE_features = None
        try:
            snippet.converging_pipelines = x_snippet.find('converging_pipelines').text
            snippet.save()
        except:
            snippet.converging_pipelines = None
        if x_snippet.find('name_pipeline').text=='True':
            snippet.name_pipeline = True
        else:
            snippet.name_pipeline = False
        if x_snippet.find('geo_pipeline').text=='True':
            snippet.geo_pipeline = True
        else:
            snippet.geo_pipeline = False
        if x_snippet.find('orgs_pipeline').text=='True':
            snippet.orgs_pipeline = True
        else:
            snippet.orgs_pipeline = False
        if x_snippet.find('topics_pipeline').text=='True':
            snippet.topics_pipeline = True
        else:
            snippet.topics_pipeline = False
        if x_snippet.find('pertinente').text=='True':
            snippet.pertinente = True
        else:
            snippet.pertinente = False
        try:
            snippet.evidence_type = x_snippet.find('evidence_type').text
            snippet.save()
        except:
            snippet.evidence_type = None
        snippet.save()
        
        



    


