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
print 'id \t name \t avg_features \t avg_strong_features \t avg_weak_features \t avg_missed_features \t evidence_type \t strong_count \t weak_count \t max_features_all \t max_features_strong \t max_features_weak \t max_features_missed' 
for p in busqueda.persona_set.all():
    strong_snippets_count = 0
    weak_snippets_count = 0
    miss_snippets_count = 0
    snippets_count = 0
    strong_feature_sum = 0
    weak_feature_sum = 0
    missed_feature_sum = 0
    all_feature_sum = 0
    avg_strong = 0.0
    avg_weak = 0.0
    avg_missed = 0.0
    avg_features = 0.0
    max_features_all = 0
    max_features_strong = 0
    max_features_weak = 0
    max_features_missed = 0
    for s in p.snippet_set.all():
        snippets_count += 1
        features_vector = bin(s.RE_features).replace('b0','')
        feature_count = 0
        for c in features_vector:
            if c=='1':
                feature_count += 1
        all_feature_sum += feature_count
        if feature_count > max_features_all:
            max_features_all = feature_count
        if s.evidence_type==1:
            strong_snippets_count += 1
            strong_feature_sum += feature_count
            if feature_count > max_features_strong:
                max_features_strong = feature_count
        elif s.evidence_type==2:
            weak_snippets_count += 1
            weak_feature_sum += feature_count
            if feature_count > max_features_weak:
                max_features_weak = feature_count
        else:
            miss_snippets_count += 1
            missed_feature_sum += feature_count
            if feature_count > max_features_missed:
                max_features_missed = feature_count
        #feature count
                
    if strong_snippets_count>0:
        evidence = 'strong'
    elif weak_snippets_count>0:
        evidence = 'weak'
    else:
        evidence = 'misssed'
    
    avg_features = float(all_feature_sum)/float(snippets_count) if snippets_count>0 else 0
    logging.debug ('calculating avg_features=' +str(all_feature_sum)+ '/' +str(snippets_count)+ '=' +str(avg_features))
    avg_strong = float(strong_feature_sum)/float(strong_snippets_count) if strong_snippets_count>0 else 0
    logging.debug ('calculating avg_strong=' +str(strong_feature_sum)+ '/' +str(strong_snippets_count)+ '=' +str(avg_strong))
    avg_weak = float(weak_feature_sum)/float(weak_snippets_count) if weak_snippets_count>0 else  0
    logging.debug ('calculating avg_weak=' +str(weak_feature_sum)+ '/' +str(weak_snippets_count)+ '=' +str(avg_weak))
    avg_missed = float(missed_feature_sum)/float(miss_snippets_count) if miss_snippets_count>0 else 0
    logging.debug ('calculating avg_missed=' +str(missed_feature_sum)+ '/' +str(miss_snippets_count)+ '=' +str(avg_missed))
    
    
    print p.id,'\t',p.name,'\t',str(avg_features),'\t',str(avg_strong),'\t',str(avg_weak),'\t',\
          str(avg_missed),'\t',evidence, '\t',strong_snippets_count,'\t',weak_snippets_count,'\t',\
          max_features_all,'\t',max_features_strong,'\t', max_features_weak,'\t',max_features_missed
    #print 'snippets_count=' +str(snippets_count)+ '\nstrong=' +str(strong_snippets_count)+\
    #      '\nweak=' +str(weak_snippets_count)+ '\nmiss=' +str(miss_snippets_count)

    #TODO IMPRIMIR LA SIGUIENTE COLUMNA
    # NOMBRE, AVG_FEATURES, AVG_STRONG_FEATURES, AVG_WEAK_FEATURES, EVIDENCE_TYPE
    

    
