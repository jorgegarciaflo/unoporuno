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
# Clasifica automáticamente a las personas según los features calculados por
# $UNPORUNO_ROOT/scripts/unoporuno_personal_feature_annotation.py
#
# usage:
# python unoporuno_svm_person_classification.py output_dir
# clasifica de acuerdo a corrida.6/emnlp2012.table6
# único algoritmo que elige top5 con una diferencia significativa
#
# lo que antes era buscado en configuration path ahora se busca en $UNOPORUNO_ROOT/resources/classifier/smo
# los archivos del clasificador son escritos en output_dir

#ejemplo:
# python run.top5.test.py 94 corrida1/ > stats.corrida1.94.csv 


__author__="Jorge García Flores"
__date__ ="$04-apr-2012 16:24:30$"


import sys, logging, ConfigParser, os, re
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
    #classifiers = ['weka.classifiers.trees.J48', 'weka.classifiers.bayes.NaiveBayes', 'weka.classifiers.trees.NBTree', 'weka.classifiers.functions.SMO', 'baseline']
    classifiers = ['weka.classifiers.functions.SMO']
    try:
        test_busqueda = sys.argv[1]
        output_path = sys.argv[2]
    except:
        logging.error('Missing output_path or test_busqueda_id')
        exit(-1)
    try:
        classifiers_file = open(sys.argv[3])
        classifiers = []
        for classifier in classifiers_file:
            classifiers.append(classifier.strip())
    except:
        pass

    for classifier in classifiers:
        clean_busqueda(test_busqueda)
        if classifier=='baseline':
            command = 'python ' +UNOPORUNO_ROOT+ '/scripts/baseline_classifier.py ' + test_busqueda
            os.system(command)
        else:
            classify_person_top5(test_busqueda, output_path, \
                             classifier, UNOPORUNO_ROOT + '/resources/classifiers/smo/models/'+classifier+'.data.model')
            
def classify_person_top5(busqueda_id, path, classifier, data_model_file):    
    output_path = path+'/'+classifier+'/'
    logging.info('classifying persons with busqueda_id='+str(busqueda_id)+', classifier'\
                  +classifier+ ' , data_model_file=' +data_model_file)
    try:
        base = DiasporaOutput(output_path)
    except:
        logging.error('Error on output path'+output_path)
        exit(-1)
    try:
        busqueda_id = int(busqueda_id)
    except:
        logging.error ('Missing busqueda_id')
        exit(-1)
    busqueda = Busqueda.objects.get(pk=busqueda_id)
    for persona in busqueda.persona_set.all():
        persona_file = base.write_personal_feature_matrix_2class(persona)
        command = 'java ' +classifier+ ' -l '+data_model_file+' -T '+persona_file+' -p 1 > '+persona_file+'.out'
        try:
            result = os.system(command)
        except:
            exit(-1)
        logging.info('classyfying with command=' + command)
    
    for subdirs, dirs, files in os.walk(output_path):
        for file in files:
            re_out = re.search('\.out$', file)
            if not re_out:
                continue
            top5 = get_weka_top5(output_path+'/'+file)
            logging.info('Extracting ' +str(len(top5))+ ' tuples from file:' +file )
            for s in top5:
                snippet = Snippet.objects.get(pk=int(s[0]))
                snippet.converging_pipelines=1
                snippet.save()
                #TODO ¿qué pasa cuando hay menos de 5 snippets?

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



def clean_busqueda(test_busqueda):
    command = 'python ' +UNOPORUNO_ROOT+ '/scripts/clean_converging_pipelines.py ' + test_busqueda
    if os.system(command)<0:
        logging.error("Couldn't clean_converging_pipelines")
        exit(-1)



    
    
    

if __name__=="__main__":
    main()
