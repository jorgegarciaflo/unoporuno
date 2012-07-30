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
      python extract_links_from_features.py (search name|search number)

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
from unoporuno.models import Busqueda, Persona, Snippet, Vinculo

if not UNOPORUNO_PATH in sys.path:
        sys.path.append(UNOPORUNO_PATH)
from dospordos.features import RegexFeature, FeatureError, \
     GazetteerFeature, QualifiedGazetteerFeature

def main():

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

    busqueda = Busqueda.objects.get(id=busqueda.id)
    for p in busqueda.persona_set.all():
        logging.info("processing person " +p.name)
        person_countries = []
        person_organizations = []
        top_snippets_count = 0
        p.vinculo_set.all().delete()
        for s in p.snippet_set.filter(FG=1).exclude(RE=1).filter(converging_pipelines=1):
            if s.FG==0 or s.RE_features<1:
                continue
            title_test_str = s.title.encode('utf-8')
            descr_test_str = s.description.encode('utf-8')
            #todo filtrar los snippets de acuerdo a las features que buscamos
            snippet_countries = []
            snippet_organizations = []
            orgs = OrganizationRegex.list_test(title_test_str)
            if len(orgs)>0:
                logging.debug ('FOUND ORGANIZATIONS ' +str(orgs)+' IN TITLE:\n ' +s.title)
                snippet_organizations += orgs
            orgs = OrganizationRegex.list_test(descr_test_str)
            if len(orgs)>0:
                logging.debug('FOUND ORGANIZATIONS ' +str(orgs)+ ' IN DESCR:\n ' +s.description)
                snippet_organizations += orgs
            accronyms = AccronymGazet.list_test(title_test_str)
            if len(accronyms)>0:
                logging.debug('FOUND ORG.ACCRONYMS ' +str(accronyms)+ ' IN TITLE:\n ' +s.title)
                snippet_organizations += accronyms
            accronyms = AccronymGazet.list_test(descr_test_str)
            if len(accronyms)>0:
                logging.debug('FOUND ORG.ACCRONYMS ' +str(accronyms)+ ' IN TITLE:\n ' +s.description)
                snippet_organizations += accronyms                
            countries = CountryGazet.list_test(title_test_str)
            if len(countries)>0:
                logging.debug ('FOUND COUNTRIES '+str(countries)+' IN TITLE:\n ' +s.title)
                snippet_countries += countries
            countries = CountryGazet.list_test(descr_test_str)
            if len(countries)>0:
                logging.debug('FOUND COUNTRIES '+str(countries)+' IN DESCR:\n ' +s.description)
                snippet_countries += countries
            countries = CountryGazetCase.list_test(title_test_str)
            if len(countries)>0:
                logging.debug ('FOUND COUNTRIES '+str(countries)+' IN TITLE:\n ' +s.title)
                snippet_countries += countries
            countries = CountryGazetCase.list_test(descr_test_str)
            if len(countries):
                logging.debug('FOUND COUNTRIES '+str(countries)+' IN DESCR:\n ' +s.description)
                snippet_countries += countries
            countries = CityGazet.list_test(title_test_str)
            if len(countries)>0:
                logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CI TITLE\n' +s.title)
                snippet_countries += countries
            countries = CityGazet.list_test(descr_test_str)
            if len(countries)>0:
                logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CI DESCRIPTION\n' +s.description)
                snippet_countries += countries
            countries = CityGazetCase.list_test(title_test_str)
            if len(countries)>0:
                logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CD TITLE\n' +s.title)
                snippet_countries += countries        
            countries = CityGazetCase.list_test(descr_test_str)
            if len(countries)>0:
                logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CD DESCRIPTION\n' +s.description)
                snippet_countries += countries
            person_countries += snippet_countries
            person_organizations += snippet_organizations
            top_snippets_count += 1
            if top_snippets_count in (5,10,15,20):
                dict_org = construye_dict_freq(person_organizations)
                dict_loc = construye_dict_freq(person_countries)
                list_org = dict_org.items()
                list_loc = dict_loc.items()
                sorted_list_org = sorted(list_org, key=lambda t:-t[1])
                sorted_list_loc = sorted(list_loc, key=lambda t:-t[1])
                organizations_str = ''
                locations_str = ''
                for e in sorted_list_org:
                    #logging.debug('type e='+str(type(e))+ ',type e[0]'+str(type(e[0]))+',e='+str(e))
                    organizations_str += e[0] + ' (' + str(e[1]) + ')\n' if len(e)>1 else ''
                for e in sorted_list_loc:
                    locations_str += e[0] + ' (' + str(e[1]) + ')\n' if len(e)>1 else ''

                logging.info('VÍNCULOS ORGANIZACIONES:: '+str(sorted_list_org))
                vinculo = Vinculo()
                vinculo.persona = p
                vinculo.organizaciones = organizations_str
                logging.info('VÍNCULOS LUGARES:: '+str(sorted_list_loc))
                vinculo.lugares = locations_str
                vinculo.descripcion = 'Top ' + str(top_snippets_count)
                vinculo.tipo = top_snippets_count
                vinculo.save()

        if top_snippets_count >= 20:
            continue
        
        for s in p.snippet_set.filter(FG=1).exclude(RE=1).exclude(converging_pipelines=1).order_by('-RE_score'):
            if s.FG==0 or s.RE_features<1:
                continue
            title_test_str = s.title.encode('utf-8')
            descr_test_str = s.description.encode('utf-8')
            #todo filtrar los snippets de acuerdo a las features que buscamos
            snippet_countries = []
            snippet_organizations = []
            orgs = OrganizationRegex.list_test(title_test_str)
            if len(orgs)>0:
                logging.debug ('FOUND ORGANIZATIONS ' +str(orgs)+' IN TITLE:\n ' +s.title)
                snippet_organizations += orgs
            orgs = OrganizationRegex.list_test(descr_test_str)
            if len(orgs)>0:
                logging.debug('FOUND ORGANIZATIONS ' +str(orgs)+ ' IN DESCR:\n ' +s.description)
                snippet_organizations += orgs
            accronyms = AccronymGazet.list_test(title_test_str)
            if len(accronyms)>0:
                logging.debug('FOUND ORG.ACCRONYMS ' +str(accronyms)+ ' IN TITLE:\n ' +s.title)
                snippet_organizations += accronyms
            accronyms = AccronymGazet.list_test(descr_test_str)
            if len(accronyms)>0:
                logging.debug('FOUND ORG.ACCRONYMS ' +str(accronyms)+ ' IN TITLE:\n ' +s.description)
                snippet_organizations += accronyms                
            countries = CountryGazet.list_test(title_test_str)
            if len(countries)>0:
                logging.debug ('FOUND COUNTRIES '+str(countries)+' IN TITLE:\n ' +s.title)
                snippet_countries += countries
            countries = CountryGazet.list_test(descr_test_str)
            if len(countries)>0:
                logging.debug('FOUND COUNTRIES '+str(countries)+' IN DESCR:\n ' +s.description)
                snippet_countries += countries
            countries = CountryGazetCase.list_test(title_test_str)
            if len(countries)>0:
                logging.debug ('FOUND COUNTRIES '+str(countries)+' IN TITLE:\n ' +s.title)
                snippet_countries += countries
            countries = CountryGazetCase.list_test(descr_test_str)
            if len(countries):
                logging.debug('FOUND COUNTRIES '+str(countries)+' IN DESCR:\n ' +s.description)
                snippet_countries += countries
            countries = CityGazet.list_test(title_test_str)
            if len(countries)>0:
                logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CI TITLE\n' +s.title)
                snippet_countries += countries
            countries = CityGazet.list_test(descr_test_str)
            if len(countries)>0:
                logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CI DESCRIPTION\n' +s.description)
                snippet_countries += countries
            countries = CityGazetCase.list_test(title_test_str)
            if len(countries)>0:
                logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CD TITLE\n' +s.title)
                snippet_countries += countries        
            countries = CityGazetCase.list_test(descr_test_str)
            if len(countries)>0:
                logging.debug('FOUND CITIES FROM COUNTRIES '+str(countries)+' IN CD DESCRIPTION\n' +s.description)
                snippet_countries += countries
            person_countries += snippet_countries
            person_organizations += snippet_organizations
            top_snippets_count += 1
            if top_snippets_count in (5,10,15,20):
                dict_org = construye_dict_freq(person_organizations)
                dict_loc = construye_dict_freq(person_countries)
                list_org = dict_org.items()
                list_loc = dict_loc.items()
                sorted_list_org = sorted(list_org, key=lambda t:-t[1])
                sorted_list_loc = sorted(list_loc, key=lambda t:-t[1])
                organizations_str = ''
                locations_str = ''
                for e in sorted_list_org:
                    #logging.debug('type e='+str(type(e))+ ',type e[0]'+str(type(e[0]))+',e='+str(e))
                    organizations_str += e[0] + ' (' + str(e[1]) + ')\n' if len(e)>1 else ''
                for e in sorted_list_loc:
                    locations_str += e[0] + ' (' + str(e[1]) + ')\n' if len(e)>1 else ''

                logging.info('VÍNCULOS ORGANIZACIONES:: '+str(sorted_list_org))
                vinculo = Vinculo()
                vinculo.persona = p
                vinculo.organizaciones = organizations_str
                logging.info('VÍNCULOS LUGARES:: '+str(sorted_list_loc))
                vinculo.lugares = locations_str
                vinculo.descripcion = 'Top ' + str(top_snippets_count)
                vinculo.tipo = top_snippets_count
                vinculo.save()
        
            if top_snippets_count >= 20:
                break


def construye_dict_freq(lista):
    d = dict()
    logging.debug('len lista=' +str(len(lista)))
    for e in lista:
        if d.has_key(e):
            d[e] += 1
        else:
            d_tmp = dict({e:1})
            d.update(d_tmp)
            logging.debug('len dictionary='+str(len(d)))
    return d
            
            
if __name__=="__main__":
    main()




