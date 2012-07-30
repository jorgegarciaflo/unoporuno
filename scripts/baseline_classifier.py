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
# usage: python features_analysis_per_person.py <person_id>

# programmed by Jorge García Flores on 16 january 2012
# LIMSI/CNRS

#very simple baseline classifier for snippets:
#esocge:
# a) los 5 snippets que tengan más features


import sys, logging, ConfigParser, time
logging.basicConfig(level=logging.INFO)
config = ConfigParser.ConfigParser()
config.read("unoporuno.conf")
UNOPORUNO_ROOT = config.get('unoporuno', 'root')
UNOPORUNO_PATH = UNOPORUNO_ROOT + '/module/'
if not UNOPORUNO_PATH in sys.path:
    sys.path.append(UNOPORUNO_PATH)

CIDESAL_WEBAPP_PATH = UNOPORUNO_ROOT + '/webapp/'
UNOPORUNO_WEBAPP_PATH = CIDESAL_WEBAPP_PATH+'cidesal/'
if not CIDESAL_WEBAPP_PATH in sys.path: 
    sys.path.append(CIDESAL_WEBAPP_PATH)
    logging.debug('cidesal web path:: ' +CIDESAL_WEBAPP_PATH)
if not UNOPORUNO_WEBAPP_PATH in sys.path:
    sys.path.append(UNOPORUNO_WEBAPP_PATH)
    logging.debug('unoporuno web path:: ' +UNOPORUNO_WEBAPP_PATH)
from unoporuno.models import Busqueda, Persona, Snippet


import sys, logging


try:
    busqueda_id = sys.argv[1]
    busqueda = Busqueda.objects.get(id=busqueda_id)
except:
    logging.error ('Bad search_id argument \n usage: python features_analysis_per_person.py <search_id>')
    exit(-1)

logging.info ('Processing search: ' + busqueda.nombre)

for p in busqueda.persona_set.all():
    tuplas_list = []
    ord_tuplas = []
    #for s in p.snippet_set.filter(FG=1, RE=0):
    for s in p.snippet_set.all():
        s.converging_pipelines = 0
        s.save()
        if s.FG==1 and s.RE==0:
            feature_count = 0
            feature_binary = bin(s.RE_features)
            features_vector = feature_binary.replace('b0','')
            logging.debug('Processing snippet:' +s.title+ ' from ' +s.query)
            for c in features_vector:
                if c=='1':
                    feature_count += 1
            tupla = (s.id,feature_count)
            tuplas_list.append(tupla)
    ord_tuplas = sorted(tuplas_list, key=lambda t:-t[1])[:5]
    for o in ord_tuplas:
        logging.info(p.name +' '+ str(o[0]) +' '+ str(o[1]))
        try:
            s = Snippet.objects.get(id=o[0])
            s.converging_pipelines = 1
            s.save()
        except:
            logging.error ("I couldn't found or save snippet number " +s.id)
            continue
    
