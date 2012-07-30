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
"""
      #TODO: WRITE A PROPER DOCUMENTATION 
      jorge.garcia-flores@limsi.fr, january 7th 2012
      usage:
      python unoporuno_personal_feature_annotation.py (search name|search number)

      Annotate unoporuno web person search snippets with the following features (per snippet)

"""

import logging, ConfigParser, sys, re

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
from dospordos.features import RegexFeature, FeatureError, \
     GazetteerFeature, QualifiedGazetteerFeature
try:
    busqueda_in = sys.argv[1]
except:
    logging.error('No parameter busqueda')
    logging.error('Usage: python batch_biographic_filter.py NAME|NUMBER path')
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
        
logging.info('Processing busqueda ' +busqueda.nombre )

#TODO: METER TODO EN UNA CLASE DENTRO DE unoporuno/modules/dospordos/features.py
OrganizationRegex = RegexFeature(UNOPORUNO_ROOT, 'organization')
CountryGazet = QualifiedGazetteerFeature(UNOPORUNO_ROOT, 'country',False)
CountryGazetCase = QualifiedGazetteerFeature(UNOPORUNO_ROOT, 'country',True)
CityGazet = QualifiedGazetteerFeature(UNOPORUNO_ROOT, 'city', False)
CityGazetCase = QualifiedGazetteerFeature(UNOPORUNO_ROOT, 'city', True)
AccronymGazet = GazetteerFeature(UNOPORUNO_ROOT, 'accronym', True)
BiophrasesRegex = RegexFeature(UNOPORUNO_ROOT, 'biographical phrases')
ProfessionRegex = RegexFeature(UNOPORUNO_ROOT, 'profession')
ProfessionGazt = GazetteerFeature(UNOPORUNO_ROOT, 'profession')
DegreeRegex = RegexFeature(UNOPORUNO_ROOT, 'degree')
DegreeGazt = GazetteerFeature(UNOPORUNO_ROOT, 'degree')
CvRegex = RegexFeature(UNOPORUNO_ROOT, 'cv general')
CvHttpRegex = RegexFeature(UNOPORUNO_ROOT, 'cv http')
LatinNatRegex = RegexFeature(UNOPORUNO_ROOT, 'latin nationalities')
WorldNatRegex = RegexFeature(UNOPORUNO_ROOT, 'world nationalities es')
WorldNatGazt = GazetteerFeature(UNOPORUNO_ROOT, 'world nationalities en')
EmailRegex = RegexFeature(UNOPORUNO_ROOT, 'email')
PublicationRegex = RegexFeature(UNOPORUNO_ROOT, 'publication')
PublicationHttpRegex = RegexFeature(UNOPORUNO_ROOT, 'publication http')
linked_re = re.compile('linkedin\.com/')
TesisRegex = RegexFeature(UNOPORUNO_ROOT, 'thesis')
TesisHttpRegex = RegexFeature(UNOPORUNO_ROOT, 'thesis http')
BlacklistHttpRegex = RegexFeature(UNOPORUNO_ROOT, 'blacklist http')

busqueda = Busqueda.objects.get(id=busqueda.id)
for p in busqueda.persona_set.all():
    logging.info("processing person " +p.name)
    #name in http pre-snippet cycle tests
    name_tokens = re.split('[ \-]', p.name)
    name_test = []
    for token in name_tokens:
        name = token.strip()
        if len(name)>2 and name not in ('del', 'von', 'DEL', 'VON'):
            name_test.append(name)
    for s in p.snippet_set.all():
        title_test_str = s.title.encode('utf-8')
        descr_test_str = s.description.encode('utf-8')
        link_test_str = s.link.encode('utf-8')        
        if s.RE_features is None:
            s.RE_features = 0
        if BlacklistHttpRegex.test(link_test_str):
            logging.debug ('FOUND blacklist REGEX IN HTTP:\n ' +s.link)
            s.RE = 1
            s.save()
            continue
        snippet_countries = []
        if OrganizationRegex.test(title_test_str):
            logging.debug ('FOUND ORGANIZATION IN TITLE:\n ' +s.title)
            s.RE_features |= 1
        if OrganizationRegex.test(descr_test_str):
            logging.debug('FOUND ORGANIZATION IN DESCR:\n ' +s.description)
            s.RE_features |= 1
        countries = CountryGazet.typed_list_test(title_test_str)
        if len(countries)>0:
            logging.debug ('FOUND COUNTRIES '+str(countries)+' IN TITLE:\n ' +s.title)
            s.RE_features |= 2
            snippet_countries += countries
        countries = CountryGazet.typed_list_test(descr_test_str)
        if len(countries)>0:
            logging.debug('FOUND COUNTRIES '+str(countries)+' IN DESCR:\n ' +s.description)
            s.RE_features |= 2
            snippet_countries += countries
        #todo: buscar países en la address ip y la nacionalidad
        countries = CountryGazetCase.typed_list_test(title_test_str)
        if len(countries)>0:
            logging.debug ('FOUND COUNTRIES '+str(countries)+' IN TITLE:\n ' +s.title)
            s.RE_features |= 2
            snippet_countries += countries
        countries = CountryGazetCase.typed_list_test(descr_test_str)
        if len(countries):
            logging.debug('FOUND COUNTRIES '+str(countries)+' IN DESCR:\n ' +s.description)
            s.RE_features |= 2
            snippet_countries += countries
        countries = CityGazet.typed_list_test(title_test_str)
        if len(countries)>0:
            logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CI TITLE\n' +s.title)
            s.RE_features |= 4
            snippet_countries += countries
        countries = CityGazet.typed_list_test(descr_test_str)
        if len(countries)>0:
            logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CI DESCRIPTION\n' +s.description)
            s.RE_features |= 4
            snippet_countries += countries
        countries = CityGazetCase.typed_list_test(title_test_str)
        if len(countries)>0:
            logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CD TITLE\n' +s.title)
            s.RE_features |= 4
            snippet_countries += countries        
        countries = CityGazetCase.typed_list_test(descr_test_str)
        if len(countries)>0:
            logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CD DESCRIPTION\n' +s.description)
            s.RE_features |= 4
            snippet_countries += countries
        if len(snippet_countries)>0:
            snippet_countries = list(set(snippet_countries))
            logging.debug('SNIPPET_COUNTRIES = '+str(snippet_countries))
            s.featured_countries = str(snippet_countries).replace('[','').replace(']','').replace("'","").replace(' ','')
        if AccronymGazet.test(title_test_str):
            logging.debug ('FOUND ACCRONYM IN TITLE:\n ' +s.title)
            s.RE_features |= 8
        if AccronymGazet.test(descr_test_str): 
            logging.debug('FOUND ACCRONYM IN DESCR:\n ' +s.description)
            s.RE_features |= 8
        if BiophrasesRegex.test(title_test_str):
            logging.debug ('FOUND BIOGRAPHICAL PHRASE IN TITLE:\n ' +s.title)
            s.RE_features |= 16
        if BiophrasesRegex.test(descr_test_str): 
            logging.debug('FOUND BIOGRAPHICAL PHRASE IN DESCR:\n ' +s.description)
            s.RE_features |= 16
        if ProfessionRegex.test(title_test_str):
            logging.debug ('FOUND PROFESSION REGEX IN TITLE:\n ' +s.title)
            s.RE_features |= 32
        if ProfessionRegex.test(descr_test_str): 
            logging.debug('FOUND PROFESSION REGEX IN DESCR:\n ' +s.description)
            s.RE_features |= 32
        if ProfessionGazt.test(title_test_str):
            logging.debug ('FOUND PROFESSION GAZT IN TITLE:\n ' +s.title)
            s.RE_features |= 32
        if ProfessionGazt.test(descr_test_str): 
            logging.debug('FOUND PROFESSION GAZT IN DESCR:\n ' +s.description)
            s.RE_features |= 32
        if DegreeRegex.test(title_test_str):
            logging.debug ('FOUND DEGREE REGEX IN TITLE:\n ' +s.title)
            s.RE_features |= 64
        if DegreeRegex.test(descr_test_str): 
            logging.debug('FOUND DEGREE REGEX IN DESCR:\n ' +s.description)
            s.RE_features |= 64
        if DegreeGazt.test(title_test_str):
            logging.debug ('FOUND DEGREE GAZT IN TITLE:\n ' +s.title)
            s.RE_features |= 64
        if DegreeGazt.test(descr_test_str): 
            logging.debug('FOUND DEGREE GAZT IN DESCR:\n ' +s.description)
            s.RE_features |= 64
        if CvRegex.test(title_test_str):
            logging.debug ('FOUND CV GENERAL REGEX IN TITLE:\n ' +s.title)
            s.RE_features |= 128
        if CvRegex.test(descr_test_str): 
            logging.debug('FOUND CV GENERAL REGEX IN DESCR:\n ' +s.description)
            s.RE_features |= 128
        if CvHttpRegex.test(link_test_str):
            logging.debug ('FOUND CV HTTP REGEX IN HTTP:\n ' +s.link)
            s.RE_features |= 128
        if CvHttpRegex.test(title_test_str): 
            logging.debug('FOUND CV HTTP REGEX  IN TITLE:\n ' +s.title)
            s.RE_features |= 128
        #name in http feature
        for test in name_test:
            re_object = re.search(test,link_test_str,flags=re.IGNORECASE)
            if re_object:
                logging.debug('FOUND NAME ' +test+ ' IN HTTP LINK:\n' \
                              +link_test_str)
                s.RE_features |= 256
                break
        if LatinNatRegex.test(title_test_str):
            logging.debug ('FOUND latin american nationality REGEX IN TITLE:\n ' +s.title)
            s.RE_features |= 512
        if LatinNatRegex.test(descr_test_str): 
            logging.debug('FOUND latin american nationality REGEX IN DESCR:\n ' +s.description)
            s.RE_features |= 512      
        if WorldNatRegex.test(title_test_str):
            logging.debug ('FOUND non latin american nationality REGEX IN TITLE:\n ' +s.title)
            s.RE_features |= 1024
        if WorldNatRegex.test(descr_test_str): 
            logging.debug('FOUND non latin american nationality REGEX IN DESCR:\n ' +s.description)
            s.RE_features |= 1024
        if WorldNatGazt.test(title_test_str):
            logging.debug ('FOUND non latin american nationality GAZT IN TITLE:\n ' +s.title)
            s.RE_features |= 1024
        if WorldNatGazt.test(descr_test_str): 
            logging.debug('FOUND non latin american nationality GAZT IN DESCR:\n ' +s.description)
            s.RE_features |= 1024
        if EmailRegex.test(title_test_str):
            logging.debug ('FOUND email REGEX IN TITLE:\n ' +s.title)
            s.RE_features |= 2048
        if EmailRegex.test(descr_test_str): 
            logging.debug('FOUND email REGEX IN DESCR:\n ' +s.description)
            s.RE_features |= 2048
        if PublicationRegex.test(title_test_str):
            logging.debug ('FOUND PUBLICATION REGEX IN TITLE:\n ' +s.title)
            s.RE_features |= 4096
        if PublicationRegex.test(descr_test_str): 
            logging.debug('FOUND PUBLICATION REGEX IN DESCR:\n ' +s.description)
            s.RE_features |= 4096
        if PublicationHttpRegex.test(link_test_str):
            logging.debug ('FOUND PUBLICATION HTTP IN LINK:\n ' +s.title)
            s.RE_features |= 4096
        re_object = linked_re.search(link_test_str)
        if re_object:
            logging.debug ('FOUND LinkedIn address IN LINK:\n ' \
                           +link_test_str)
            s.RE_features |= 8192
        if TesisHttpRegex.test(link_test_str):
            logging.debug ('FOUND TESIS HTTP IN LINK:\n ' +s.title)
            s.RE_features |= 16384 
        if TesisRegex.test(title_test_str):
            logging.debug ('FOUND TESIS REGEX IN TITLE:\n ' +s.title)
            s.RE_features |= 16384
        if TesisRegex.test(descr_test_str): 
            logging.debug('FOUND TESIS REGEX IN DESCR:\n ' +s.description)
            s.RE_features |= 16384
        s.save()

            
            





