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
# usage: python unoporuno_export.py (name|number) [person_id_file]results_path
# exports a unoporuno database to an xml file following unopourno DTD
# if a person_id_file is present, it exports only those id's indicated in the file


import logging, ConfigParser, sys

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
from dospordos.tools import DiasporaOutput
try:
    busqueda_in = sys.argv[1]
except:
    logging.error('No parameter busqueda')
    logging.error('Usage: python unoporuno_export.py NAME|NUMBER path')
    exit(-1)
    
if busqueda_in.isdigit():
    try:
        busqueda = Busqueda.objects.get(id=int(busqueda_in))
    except:
        logging.error('No busqueda object with id=' +busqueda_in+ ' in UNOPORUNO database.')
        exit(-1)
else:
    try:
        busqueda = Busqueda.objects.get(nombre=busqueda_in)
    except:
        logging.error('No busqueda object with id=' +busqueda_in+ ' in UNOPORUNO database.')
        exit(-1)

        
logging.info('Cleaning converging pipelines for busqueda ' +busqueda.nombre )
for persona in busqueda.persona_set.all():
    logging.debug('cleaning person ' +persona.name)
    for s in persona.snippet_set.filter(converging_pipelines__gt=0):
        s.converging_pipelines=0
        s.save()
    persona.mobility_status = None
    persona.save()
