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
# fusiona todos los nombres repetidos en una búsqueda
# usage:
# python fussion_repeated_persons.py 78 lista.repetidos.txt
# 78 es el número de la búsqueda
# lista repetidos es un .txt con los nombres de los investigadores


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
    
    try:
        busqueda_id = int(sys.argv[1])
        busqueda = Busqueda.objects.get(id=int(busqueda_id))
    except:
        logging.error('Missing search number')
        exit(-1)
        
    try:
        nombres_repetidos_file = open(sys.argv[2])
    except:
        logging.error('Missing repeated names list')
        exit(-1)

    #1: busco el id de la primera persona
    #2: hago un ciclo con los homonimos
    #3: cojo todos los snippets del homonimo
    #4: les actualizo el person-id con el de laprimera persona
    logging.info('processing busqueda_id='+str(busqueda_id)+' with repeated persons list='+sys.argv[2])
    for nombre in nombres_repetidos_file:
        lista_homonimos = list(busqueda.persona_set.filter(name=nombre.strip()))
        logging.info('Fusionando '+nombre.strip()+' con '+ str(len(lista_homonimos))+ ' repeticiones')
        if lista_homonimos <=1:
            continue
        primero = lista_homonimos.pop(0)
        logging.info('persona id del primero =' +str(primero.id))
        for homonimo in lista_homonimos:
            for s in homonimo.snippet_set.all():
                s.persona_id = primero.id
                s.save()
            homonimo.delete()
        
if __name__=="__main__":
    main()
