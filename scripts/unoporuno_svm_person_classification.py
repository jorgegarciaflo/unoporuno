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
# python unoporuno_svm_person_classification.py id_busqueda output_dir
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
    #TODO: validar cuando a) no hay snippets clasificados como positivos y b) hay menos de 5 snippets clasificados como positivos

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
    d_personas = dict()
    for persona in busqueda.persona_set.all():
        persona_file = persona_file = base.write_personal_feature_matrix_2class(persona)
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
            classed_snippets = get_weka_top5(output_path+'/'+file)
            logging.info('Extracting ' +str(len(classed_snippets))+ ' tuples from file:' +file ) 
            
            if len(classed_snippets):
                for s in classed_snippets[0]:
                    snippet = Snippet.objects.get(pk=int(s[0]))
                    if d_personas.has_key(snippet.persona_id):
                        d_paises = d_personas[snippet.persona_id]
                    else:
                        d_paises = dict()
                    lista_paises = snippet.featured_countries.split(',') if snippet.featured_countries else []
                    for pais in lista_paises:
                        u_pais = pais.encode('utf-8')
                        if d_paises.has_key(u_pais):
                            d_paises[u_pais] += 1
                        else:
                            d_pais = dict({u_pais:1})
                            d_paises.update(d_pais)
                    d_persona = dict({snippet.persona_id:d_paises})
                    d_personas.update(d_persona)


                for s in classed_snippets[0]:
                    snippet = Snippet.objects.get(pk=int(s[0]))
                    snippet.converging_pipelines=2
                    snippet.RE_score = str(s[1]) 
                    snippet.RE_score = get_feature_count(snippet.RE_features)
                    snippet.save()
                    
            if len(classed_snippets)>1:
                for s in classed_snippets[1]:
                    snippet = Snippet.objects.get(pk=int(s[0]))
                    snippet.converging_pipelines=3
                    snippet.RE_score = str(s[1]) 
                    snippet.RE_score = get_feature_count(snippet.RE_features)
                    snippet.save()

    LA = ['AR','BZ','BO','CL','CO','CR','C','DO','SV','MX','GT','HT','JM','NI','PY','PE','VE','TT','PY','HN','PA','UY']

    for persona in busqueda.persona_set.all():

        if not d_personas.has_key(persona.id):                      
            d_paises = dict()
            d_persona = dict({persona.id:d_paises})
            d_personas.update(d_persona)
        
        logging.info('Persona ' +persona.name+ ' has the following country frequencies:' +str(d_personas[persona.id])+ \
                     ' and mobility_status='+str(persona.mobility_status))
        LA_freq = ('',0)
        mundo_freq = ('',0)
        for pais in d_personas[persona.id].keys():
            u_pais = pais.encode('utf-8')            
            if u_pais in LA:
                if d_personas[persona.id][u_pais] > LA_freq[1]:
                    LA_freq = (u_pais,d_personas[persona.id][u_pais])
            else:
                if d_personas[persona.id][u_pais] > mundo_freq[1]:
                    mundo_freq = (u_pais, d_personas[persona.id][u_pais])
        logging.info('Pais LA mas frequente:' +str(LA_freq))
        logging.info('Pais no LA mas frequente:' +str(mundo_freq))

        #3 del país móvil más frecuente
        #2 del país latinoamericano más frecuente
        #los demás con móviles
        if mundo_freq[1]>0 and LA_freq[1]>0:
            persona.mobility_status=1
            logging.info(persona.name+' is movil! with mobility_status=' +str(persona.mobility_status))            
        elif mundo_freq[1]>0 or LA_freq[1]>0:
            persona.mobility_status = 0
            logging.info('local!')
        else:
            persona.mobility_status = 3
            logging.info('no sé!')
        
        
        mobile_snippets = persona.snippet_set.filter(converging_pipelines=2).order_by('-RE_score')
        local_snippets = persona.snippet_set.filter(converging_pipelines=3).order_by('-RE_score')    
        converging_count = [0,0,0] #[converging_count, world_count, LA_count]
        if mundo_freq[1]>0:
            mobile_limit = min(3,mundo_freq[1])
            LA_limit = min(2,LA_freq[1])
            for s in mobile_snippets:
                if converging_count[0]>=5:
                    break
                if converging_count[1]<mobile_limit:
                    if mundo_freq[0] in str(s.featured_countries):
                        s.converging_pipelines=1
                        s.save()
                        converging_count[0]+=1
                        converging_count[1]+=1
                        logging.info('world hit!')
                elif converging_count[2]<LA_limit:
                    if LA_freq[0] in str(s.featured_countries):
                        s.converging_pipelines=1
                        s.save()
                        converging_count[0]+=1
                        converging_count[2]+=1
                        logging.info('LA hit!')
            if converging_count[0]<5:
                for s in local_snippets:
                    if converging_count[0]>=5:
                        break
                    if converging_count[1]<mobile_limit:
                        if mundo_freq[0] in str(s.featured_countries):
                            s.converging_pipelines=1
                            s.save()
                            converging_count[0]+=1
                            converging_count[1]+=1
                            logging.info('world local hit!')
                    elif converging_count[2]<LA_limit:
                        if LA_freq[0] in str(s.featured_countries):
                            s.converging_pipelines=1
                            s.save()
                            converging_count[0]+=1
                            converging_count[2]+=1
                            logging.info('LA local hit!')
        if converging_count[0]<5:
            for s in mobile_snippets:
                if converging_count[0]>=5:
                    break
                if s.converging_pipelines==1:
                    continue
                s.converging_pipelines=1
                s.save()
                converging_count[0]+=1
        if converging_count[0]<5:
            for s in local_snippets:
                if converging_count[0]>=5:
                    break
                if s.converging_pipelines==1:
                    continue
                s.converging_pipelines=1
                s.save()
                converging_count[0]+=1
        if converging_count[0]<5:
            todos = persona.snippet_set.filter(FG=1).exclude(RE=1).order_by('-RE_features')
            for s in local_snippets:
                if converging_count[0]>=5:
                    break
                if s.converging_pipelines==1:
                    continue
                s.converging_pipelines=1
                s.save()
                converging_count[0]+=1
        if converging_count<5:
            for s in local_snippets:
                if converging_count>=5:
                    break
                s.converging_pipelines=1
                s.save()
                converging_count +=1
        logging.info(persona.name+' is movil! with mobility_status=' +str(persona.mobility_status))
        persona.save()

            
## OLD USELESS PERSON FUNCTION 
## def classify_person_top5(busqueda_id, path, classifier, data_model_file):    
##     output_path = path+'/'+classifier+'/'
##     logging.info('classifying persons with busqueda_id='+str(busqueda_id)+', classifier'\
##                   +classifier+ ' , data_model_file=' +data_model_file)
##     try:
##         base = DiasporaOutput(output_path)
##     except:
##         logging.error('Error on output path'+output_path)
##         exit(-1)
##     try:
##         busqueda_id = int(busqueda_id)
##     except:
##         logging.error ('Missing busqueda_id')
##         exit(-1)
##     busqueda = Busqueda.objects.get(pk=busqueda_id)
##     for persona in busqueda.persona_set.all():
##         persona_file = base.write_personal_feature_matrix_2class(persona)
##         command = 'java ' +classifier+ ' -l '+data_model_file+' -T '+persona_file+' -p 1 > '+persona_file+'.out'
##         try:
##             result = os.system(command)
##         except:
##             exit(-1)
##         logging.info('classyfying with command=' + command)
    
##     for subdirs, dirs, files in os.walk(output_path):
##         for file in files:
##             re_out = re.search('\.out$', file)
##             if not re_out:
##                 continue
##             top5 = get_weka_top5(output_path+'/'+file)
##             logging.info('Extracting ' +str(len(top5))+ ' tuples from file:' +file )
##             for s in top5:
##                 snippet = Snippet.objects.get(pk=int(s[0]))
##                 snippet.converging_pipelines=1
##                 snippet.save()
##                 #TODO ¿qué pasa cuando hay menos de 5 snippets?

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
    #TODO: si son menos de 5, completar con el resto
    return ord_tuplas



def clean_busqueda(test_busqueda):
    command = 'python ' +UNOPORUNO_ROOT+ '/scripts/clean_converging_pipelines.py ' + test_busqueda
    if os.system(command)<0:
        logging.error("Couldn't clean_converging_pipelines")
        exit(-1)



    
    
    

if __name__=="__main__":
    main()
