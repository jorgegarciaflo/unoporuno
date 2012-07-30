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
# usage: python converging_pipelines.py input_file.csv output_folder
#        input_file.xml = persons to search
# programmed by Jorge García Flores on 1st june 2011
# LIMSI/CNRS

import sys, logging, ConfigParser, time
logging.basicConfig(level = logging.INFO)
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


import sys
busqueda_in = sys.argv[1]
if busqueda_in.isdigit():
    busqueda = Busqueda.objects.get(id=busqueda_in)
else:
    busqueda = Busqueda.objects.get(nombre=busqueda_in)


print 'ID,tesis,linkedin,publication,email,world_nat,latin_nat,name_in_http,cv,degree,prof,bio,accro,city,country,org,class'
for p in busqueda.persona_set.all():
    logging.debug("processing person " +p.name)
    for s in p.snippet_set.filter(FG=1).exclude(RE=1):
        if s.evidence_type is None:
            evidence_type = '0'
        else:
            evidence_type = str(s.evidence_type)
        if s.RE_features is None:
            RE_features = '0'
        else:
            RE_features = str(bin(int(s.RE_features))).replace('0b','')
            """
            if len(RE_features)<15:
		    fill_0 = 15-len(RE_features)
		    fill_list = range(fill_0)
		    for f in fill_list:
			    RE_features += '0'
	"""
	
        features = str(RE_features.zfill(15))
        features_str = ''
        for c in features:
            features_str += c+','
        print_str = str(s.id) + ',' + features_str + str(evidence_type)
        print print_str
