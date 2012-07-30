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
# Exporta archivos personales de features en formato .arff (weka)
# Clasifica 

__author__="Jorge García Flores"
__date__ ="$08-oct-2011 10:05:30$"

import sys, logging, ConfigParser, time, os, re
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
    
if not UNOPORUNO_WEBAPP_PATH in sys.path:
    sys.path.append(UNOPORUNO_WEBAPP_PATH)
    logging.debug('unoporuno web path:: ' +UNOPORUNO_WEBAPP_PATH)
from dospordos.tools import DiasporaOutput
from unoporuno.models import Busqueda, Persona, Snippet

def main():

    try:
        base = DiasporaOutput(sys.argv[1])
    except:
        logging.error('Missing output path')
        exit(-1)
    try:
        busqueda_id = int(sys.argv[2])
    except:
        logging.error ('Missing busqueda_id')
        exit(-1)
    busqueda = Busqueda.objects.get(pk=busqueda_id)
    for persona in busqueda.persona_set.all():
        person_file = base.write_personal_feature_matrix(persona)
        logging.info('Exporting features matrix for person ' +persona.name)
        # TODO: reconnaitre 32 bits et 64 bits data model
        # j48_path = UNOPORUNO_ROOT + '/resources/classifiers/j48/J48.weka.32.data.model'
        nbtree_path = UNOPORUNO_ROOT + '/resources/classifiers/naivebayes/NaiveBayes.data.model'
        command = 'java weka.classifiers.bayes.NaiveBayes -l '+nbtree_path+' -T '+person_file+' -p 1 > '+person_file+'.out'
        logging.info('classyfying with command=' + command)
        try:
            result = os.system(command)
        except:
            exit(-1)

    for subdirs, dirs, files in os.walk(sys.argv[1]+'/'):
        for file in files:
            re_out = re.search('\.out$', file)
            if not re_out:
                continue
            top5 = get_weka_top5(sys.argv[1]+'/'+file)
            logging.info('Extracting ' +str(top5)+ ' tuples from file:' +file )
            for s in top5:
                snippet = Snippet.objects.get(pk=int(s[0]))
                snippet.converging_pipelines=1
                snippet.save()



def get_weka_top5(file_name):
    logging.info('extracting top 5 from ' +file_name)
    strong_evidence = []
    try:
        f=open(file_name, 'r')
    except:
        return strong_evidence
    for line in f:
        columns = re.split(' +', line.strip())
        if len(columns)>1:
            if columns[2]=='2:1':
                #print columns
                if columns[3]=='+':
                    prediction = float(columns[4])
                    snippet_id = re.sub('[()]','',columns[5])
                else:
                    prediction = float(columns[3])
                    snippet_id = re.sub('[()]','',columns[4])
                tupla = (snippet_id, prediction)
                strong_evidence.append(tupla)
    ord_tuplas = sorted(strong_evidence, key=lambda t:-t[1])[:5]
    return ord_tuplas
        
# persona = Persona.objects.get(pk=busqueda_id)
# F = base.write_personal_feature_matrix(persona)
# logging.debug('Exporting features matrix for person ' +str(persona.id))

if __name__=="__main__":
    main()

