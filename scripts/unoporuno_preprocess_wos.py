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
#      programmed by jorge.garcia-flores@limsi.fr on december 2011
# goal: TODO: TREAT A WOS EXCEL TYPE FILE, COMO EL QUE VAMOS A USAR PARA EL EXPERIMENTO DE LOS 2000 URUGUAYOS
#       select spanish name authors from a wos publications file and create a unoporuno friendly csv file
# wos field order in file:
# PT AU BA ED GP AF CA TI SO SE LA DT CT CY CL SP HO DE ID AB C1 RP EM FU FX CR NR TC PU PI PA SN BN DI J9 JI PD PY VL IS PN SU SI BP EP AR DI PG SC GA UT
#
# TODO: si la palabra está en inglés, se busca la abreviación en inglés
#       arreglar las putas abreviaciones de WoS
#       arreglar el reconocimiento y la traducción de ciudades y países

# usage:
# python preprocess_wos_input.py wos_file.txt [all] > unoporuno_input.csv

#TODO:
#bug
#000256860000013|B. F. Giannetti|Platinum surface modification with cerium species and the effect against the methanol anodic reaction|Instituto Ciencias Exatas & Tecnologia;LaFTA;University Estadual Paulista;Sao Paulo;Laboratorio Fisicoquim Teor & Aplicada|Brazil;
#cuando hay un sólo autor (y acaso un solo país) no traduce el país


__author__="Jorge García Flores"
__date__ ="$29-dec-2011 23:05:$"

import sys, re, logging, ConfigParser, os

logging.basicConfig(level=logging.DEBUG)
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
if not UNOPORUNO_PATH in sys.path:
        sys.path.append(UNOPORUNO_PATH)
from dospordos.tools import DetectaLengua

def main():
    logging.basicConfig(level=logging.DEBUG)

    world = World()
    abbrev = Abbreviation()

    spanish_names = read_spanish_names(UNOPORUNO_ROOT)
    logging.debug ('spanish name list has ' +str(len(spanish_names)) +' names')
    wos_file = open(sys.argv[1])
    try:
        authors_filter = False if sys.argv[2]=='all' else True
    except:
        authors_filter = True
    
    
    records = []
    #record_limit = re.compile (r'\*Record [0-9]+ of [0-9]+\.')
    buffer = ''
    for wos_line in wos_file:
        wos_line=re.sub ('"',"'",wos_line)
        article = str.rsplit(wos_line, '|')    
# II: split fields
        if len(article) >= 24 :
            #article_num = article[0]
            publication_type = article[0] #WoS_code: PT
            authors = article[1] #AU
            if len(article[5].strip())>0:
                authors_full = article[5] #AF
            else:
                authors_full = authors
            document_title = article[7] #TI
            publication_name = article[8] #SO
            language = article [10] #LA
            document_type = article[11] #DT
            author_keywords = article[17] #DE
            keyword_plus = article[18] #ID
            affiliation_string = article[20] #C1 ** this is the one we want **
            reprint_address = article[21] #RP
            email_address = article[22] #EM
            publisher = article [28] #PU
            publisher_city = article [29] #PI
            publisher_address = article[30] #PA
            publication_date = article[36] #PD
            publication_year = article[37] #PY
            subject_category = article[48] #SC
            delivery_number = article[49] #GA
            unique_identifier = article[50] #UT
            
            title = document_title
            authors_list = wos_parse_authors_full_name(authors_full)
            logging.debug('Processing title:' +title)

            affiliation = Affiliation(affiliation_string, abbrev, world, authors_list)

            # Dos casos:
            # a) En la afiliación hay al menos un país no latinoamericano:
            #          se seleccionan solamente investigadores con nombre o apellido hispánico
            # b) En la afiliación hay sólo países latinoamericanos
            #          se seleccionan todos los investigadores
            
            for team in affiliation.teams:
                logging.debug('Team loop: processing ' + str(team.members) +'\n Affiliation_set:' +str(team.affiliation))
                latin_american_only = True
                geo_list = []
                orgs_list = []
                for aff in team.affiliation:
                    if world.is_country(aff):
                        geo_list.append(aff)
                        #logging.debug('Candidate ' +aff+ ' is a country!')
                        if not world.is_latin_american(aff):
                            #logging.debug(aff + 'is not a latin american country!')
                            latin_american_only = False
                        aff_translation = world.translate_country(aff)
                        if aff_translation:
                            geo_list.append(aff_translation)
                            logging.debug('Translating country ' +aff+ ' into ' +aff_translation)
                    elif world.is_city(aff):
                        #logging.debug('Candidate ' +aff+ ' is a city or a state!')
                        geo_list.append(aff)
                        if world.is_american(aff):
                            latin_american_only = False
                    else:
                        orgs_list.append(aff)
                #cheap trick not to filter authors if the -all parameter is present
                if not authors_filter:
                    latin_american_only = True
                    logging.debug('No filter for authors with spanish names')
                if not latin_american_only:
                    logging.debug('International team: processing only authors with spanish names')
                    spanish_authors_list=[]
                    for t in team.members:
                        logging.debug('Processing author:' +t)
                        # para seleccionar sólo los autores con nombre completo o con iniciales
                        # TODO: parametrar
                        #if authors_full != authors:
                        #    continue
                        if is_spanish_author(t, spanish_names):
                            logging.debug('Spanish author found! ' +t)
                            orgs = ';'.join(orgs_list)
                            geo = ';'.join(geo_list)
                            logging.debug ('Name=' +t)
                            logging.debug('Organizations=' +orgs)
                            logging.debug('Geography=' +geo)
                            logging.debug('Topics=' +title)
                            print unique_identifier.replace('ISI:','').strip() + '|'  +t.strip()+ '|'\
                                  +title.strip()+ '|' +orgs.strip()+ '|' +geo.replace(';;',';').strip() 
                else:
                    logging.debug('Latin american team: processing all authors')
                    for t in team.members:
                        logging.debug('Processing author:' +t)
                        # para seleccionar sólo los autores con nombre completo o con iniciales                         
                        #if authors_full == authors:
                        #    continue
                        orgs = ';'.join(orgs_list)
                        geo = ';'.join(geo_list)
                        logging.debug ('Name=' +t)
                        logging.debug('Organizations=' +orgs)
                        logging.debug('Geography=' +geo)
                        logging.debug('Topics=' +title)
                        print unique_identifier.replace('ISI:','').strip() + '|'  +t.strip()+ '|'\
                              +title.strip()+ '|' +orgs.strip()+ '|' +geo.replace(';;',';').strip() 
                    
    exit(0)
    
## ****** MAIN PUBLICATIONS LOOP ***********

                        
def read_spanish_names(root):
#fills a list with all spanish first and lastnames present in HELLO_ROOT/resources
    names_list = []
    first_file = root + "/resources/spanish_firstnames.txt"
    last_file = root + "/resources/spanish_lastnames.txt"
    F = open(first_file)
    for f in F:
        names_list.append(f.strip())
    L = open(last_file)
    for l in L:
        names_list.append(l.strip())
    return names_list

def wos_parse_authors_full_name(wos_name):
    authors_list = []
    authors = wos_name.split(';')
    for author in authors:
        names=author.split(',')
        if len(names)>=2:
            full_name = names[1].strip() + ' ' + names[0].strip()
        else:
            full_name = names[0]
        if len(names)>=2: authors_list.append(full_name)
    return authors_list


def is_spanish_author(author, spanish_names):
    tokens = re.split('[ \-]', author)
    for t in tokens:
        if t.strip() in spanish_names:
            return True
    return False


class World:
    #TODO: extender la lista de ciudades
    #TODO: cuidar los acentos en las ciudades
    def __init__(self, countries=UNOPORUNO_ROOT+'/resources/country_names.en.es.local.txt', cities=UNOPORUNO_ROOT+'/resources/gazetteer/100mil.ciudades.cd.gazt'):        
        global UNOPORUNO_ROOT
        self.countries_es = []
        self.countries_en = []
        self.cities = []
        countries = open(countries)
        for country in countries:
            triplet=country.split(',')
            if len(triplet)>=2:
                self.countries_en.append(triplet[0].strip().capitalize())
                self.countries_es.append(triplet[1].strip().capitalize())
        cities = open(cities)
        for city in cities:
            self.cities.append(city.strip().capitalize())
        logging.debug('Read ' +str(len(self.cities))+ ' cities from file')
            
    def is_country(self, country, lang='both'):
        country = re.subn('[\.,;]', '', country)[0]
        logging.debug('searching country ' +country+ ' in country list')
        if lang=='es':
            if country.strip().capitalize() in self.countries_es:
                return True
            else:
                return False
        elif lang=='en':
            if country.strip().capitalize() in self.countries_en:
                return True
            else:
                return False
        else:
            c = country.strip().capitalize()
            if (c in self.countries_es) or (c in self.countries_en):
                return True
            else:
                return False

    def is_city(self, city):
        if city.strip().capitalize() in self.cities:
            return True
        else:
            return False

# correct list contains Brazil, la quitamos para efectos del experimento de los 2000 uruguayos
#LA_list = ['Argentina','Bolivia','Brasil','Brazil','Chile','Colombia','Costa Rica','Dominicana',\
    def is_latin_american(self,country):
        country = re.subn('[\.,;]', '', country)[0]
        LA_list = ['Argentina','Bolivia','Chile','Colombia','Costa Rica','Dominicana',\
                   'Republica Dominicana','Dominican Republic','Ecuador','El Salvador','Honduras','Mexico',\
                   'Nicaragua','Cuba','Haiti','Peru','Uruguay','Venezuela','Paraguay','Panama']
        if country.strip() in LA_list:
            return True
        else:
            return False

    def is_american(self,country):
        country = re.subn('[\.,;]', '', country)[0]
        USA_list = ['Alaska','Alabama','Arkansas','Arizona','California','Colorado','Connecticut','District of Columbia',\
                    'Delaware','Florida','Georgia','Hawaii','Iowa','Idaho','Illinois','Indiana','Kansas','Kentucky',\
                    'Louisiana','Massachusetts','Maryland','Maine','Michigan','Minnesota','Missouri','Mississippi',\
                    'Montana','North Carolina','North Dakota','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico',\
                    'New York','Ohio','Oklahoma','Oregon','Pennsylvania','Puerto Rico','Rhode Island','South Carolina',\
                    'South Dakota','Tennessee','Texas','Utah','Virginia','Vermont','Washington','Wisconsin',\
                    'West Virginia','Wyoming']
        if country.strip() in USA_list:
            return True
        else:
            return False
#TODO: translate city
    def translate_country(self, eng_country):
        trans_table = {'Austria': 'Österreich','Belgium':'Bélgica;Belgique;Belgie','Brazil':'Brasil','Cambodia':'Camboya',
                       'Korea':'Corea','Croatia':'Croacia','Denmark':'Dinamarca;Danmark','Egypt':'Egipto','Finland':'Finlandia',\
                       'France':'Francia','Germany':'Alemania;Deutschland','Great Britain':'Gran Bretaña','England':'Inglaterra',\
                       'Greece':'Grecia','Iceland':'Islandia','Ireland':'Irlanda','Italy':'Italia','Japan':'Japón','Jordan':'Jordania',\
                       'Lebanon':'Líbano','Luxembourg':'Luxemburgo','New Zealand':'Nueva Zelanda','Norway':'Noruega;Norge',\
                       'Philippines':'Filipinas','Russia':'Rusia','Singapore':'Singapur','South Africa':'Sudáfrica','Spain':'España',\
                       'Scotland':'Escocia','Turkey':'Turquía','Tunisia':'Túnez','Latvia':'Letonia','Lithuania':'Lituania',\
                       'Czech Republic':'República Checa','Slovakia':'Eslovaquia','Slovenia':'Eslovenia',\
                       'Netherlands':'Holanda;Nederland','Sweden':'Suecia'}
        if eng_country in trans_table:
            return trans_table[eng_country]
        else:
            return ''
    
class Abbreviation:
    #process abbreviations and takes out postal codes!
    def __init__ (self,spanish_file=UNOPORUNO_ROOT+'/resources/wos.abbrev.es.txt', \
                  english_file=UNOPORUNO_ROOT+'/resources/wos.abbrev.world.txt',
                  usa_file=UNOPORUNO_ROOT+'/resources/wos.us.states.abb.txt'):
        global UNOPORUNO_ROOT
        self.abb_es = dict()
        f_es = open(spanish_file)
        for line in f_es:
            pair = line.split(',')
            if len(pair)>1: self.abb_es[pair[1].strip()]=pair[0].strip()
        #print 'SPANISH DICT LEN =', len(self.abb_es)
        self.abb_en = dict()
        f_en = open(english_file)
        for line in f_en:
            pair = line.split(',')
            if len(pair)>1: self.abb_en[pair[1].strip()]=pair[0].strip()
        #print 'ENGLISH DICT LEN =', len(self.abb_en)
        self.abb_us = dict()
        f_en = open(usa_file)
        for line in f_en:
            pair = line.split(',')
            if len(pair)>1: self.abb_us[pair[1].strip()]=pair[0].strip()
        
        self.uk_postal=re.compile (r'(GIR 0AA|[A-PR-UWYZ]([0-9]{1,2}|(WA-HK-Y][0-9]|[A-HK-Y][0-9]([0-9]|[ABEHMNPRV-Y]))|[0-9][A-HJKPS-UW]) [0-9][ABD-HJLNP-UW-Z]{2})')
        self.arg_postal=re.compile(r'[A-Z][A-Z]-[0-9]+')
        self.eur_postal=re.compile(r'[A-Z]-[0-9]+')
        self.us_postal=re.compile(r'[0-9]+')
        self.usa=re.compile(r'([A-Z][A-Z])[ ]+USA;?')
        logging.info('Slowly loading language detector' )
        self.lang_detector = DetectaLengua(UNOPORUNO_ROOT+'/resources/dictionaries/nltk_cess_esp.vocab')
        logging.info('Language detector loaded!')


"""
class Affiliation:
   Dos casos por tratar en class Affiliation:
   a) affiliaciones separadas por ; (desordenadas)
   Cada autor lleva todas las afiliaciones. Un sólo equipo con una afiliación en donde se cocentran todas

   b) afiliaciones separadas por [ (ordenadas)
   Autor: Soutullo, A; Gudynas, E
   affiliation_string: Univ Alicante, CIBIO, Fdn Terra Natura, E-03080 Alicante, Spain; CLAES, Montevideo 11700, Uruguay
"""
        
class Affiliation:
    def __init__(self, affiliation_string, abbv, world, authors_list):
        self.teams = []
        self._affiliation_string = affiliation_string.strip()
        self._authors = []
        self._institutions=[]
        self._places = []
        self._len_authors = len(authors_list)
        self._authors_list = authors_list
        self.parse_affiliation(abbv)
        

    def parse_affiliation(self, abbv):
        team_list = []
        if self._affiliation_string.find('[')>=0:
            team_list = self._affiliation_string.split('[')
            for team in team_list:
                logging.debug('Processing team member:' +team)
                if team:
                    affiliation_tuple = team.split(']')
                    logging.debug('affiliation_tuple=' +str(affiliation_tuple))
                    if len(affiliation_tuple)>1:
                        self._authors = wos_parse_authors_full_name(affiliation_tuple[0].strip())
                        #taking out postal codes before proceeding
                        clean_aff = abbv.uk_postal.sub('', affiliation_tuple[1])
                        clean_aff = abbv.arg_postal.sub('' , clean_aff)
                        clean_aff = abbv.eur_postal.sub('', clean_aff)
                        clean_aff = abbv.us_postal.sub('', clean_aff)
                        searching = abbv.usa.search(clean_aff)
                        if searching:
                            state_abv = searching.group(1)
                            state = abbv.abb_us[state_abv]
                            clean_aff = abbv.usa.sub(state,clean_aff)
                        self._institutions = self._affiliation_split(clean_aff.strip())
                        self._queries = self._process_abbreviations(self._institutions, abbv)
                        if self._authors and self._queries:
                            team = Team(self._authors, self._queries, self._affiliation_string)
                            self.teams.append(team)
        else:
            # si no hay organización de autores por institución, vamos a ser tantos equipos como instituciones haya
            # poniendo en cada equipo todos los autores
            # tant pis
            logging.debug('One team processing for article, authors_len=' +str(self._len_authors)+ '\n affiliation_string: ' +self._affiliation_string+ \
                          '\n authors_list=' +str(self._authors_list))
            self._authors = self._authors_list
            #if self._affiliation_string.find(';')>=0:
            #    mixed_aff_list = self._affiliation_string.split(';')
            #    for aff in mixed_aff_list:
            aff = self._affiliation_string.replace(';',',')
            logging.debug('Processing affiliation ' +aff+ ' for unique team')
            clean_aff = abbv.uk_postal.sub('', aff.strip())
            clean_aff = abbv.arg_postal.sub('' , clean_aff)
            clean_aff = abbv.eur_postal.sub('', clean_aff)
            clean_aff = abbv.us_postal.sub('', clean_aff)
            searching = abbv.usa.search(clean_aff)
            if searching:
                state_abv = searching.group(1)
                state = abbv.abb_us[state_abv]
                clean_aff = abbv.usa.sub(state,clean_aff)
            self._institutions = self._affiliation_split(clean_aff.strip())
            self._queries = self._process_abbreviations(self._institutions, abbv)
            if self._authors and self._queries:
                team = Team(self._authors, self._queries, self._affiliation_string)
                self.teams.append(team)
                    

    def _process_abbreviations(self, phrases, abv):

        #TODO: primero expandir la abreviación, luego probar la lengua
 
        queries = set()
        for phrase in phrases:
            buffer_es = ''
            buffer_en = ''
            tokens = phrase.split()
            spanish_count = 0
            english_count = 0
            for token in tokens:
                if abv.abb_es.has_key(token):
                    buffer_es = buffer_es + ' ' + abv.abb_es[token]
                    spanish_count += 1
                else:
                    buffer_es = buffer_es + ' ' + token
                if abv.abb_en.has_key(token):
                    buffer_en = buffer_en + ' ' + abv.abb_en[token]
                    english_count += 1
                else:
                    buffer_en = buffer_en + ' ' + token
            logging.debug('buffer_eng: ' +buffer_en+ ' in language ' +abv.lang_detector.lengua(buffer_en))
            logging.debug('buffer_esp: ' +buffer_es+ ' in language ' +abv.lang_detector.lengua(buffer_es))
            if buffer_en == buffer_es:
                queries.add(buffer_en.strip())
                logging.debug ('adding egality to buffer::' +buffer_en.strip())
            else:
                lang_buffer_en = abv.lang_detector.lengua(buffer_en)
                lang_buffer_es = abv.lang_detector.lengua(buffer_es)
                if lang_buffer_en == 'eng' and lang_buffer_es != 'esp':
                    logging.debug ('adding english to buffer' +buffer_en.strip())
                    queries.add(buffer_en.strip())
                elif lang_buffer_es == 'esp' and lang_buffer_en != 'eng':
                    logging.debug ('adding spanish to buffer' +buffer_es.strip())                    
                    queries.add(buffer_es.strip())
                else:
                    if spanish_count < english_count:
                        logging.debug ('adding english {esp=' +str(spanish_count)+ ', eng=' +str(english_count)+'} to buffer::' +buffer_en.strip())        
                        queries.add(buffer_en.strip())
                    elif english_count < spanish_count:
                        logging.debug ('adding spanish {esp=' +str(spanish_count)+ ', eng=' +str(english_count)+'} to buffer::' +buffer_es.strip())        
                        queries.add(buffer_es.strip())
                    else:
                        logging.debug ('adding english {esp=' +str(spanish_count)+ ', eng=' +str(english_count)+'} to buffer::' +buffer_en.strip())       
                        queries.add(buffer_en.strip())
                        logging.debug ('adding spanish {esp=' +str(spanish_count)+ ', eng=' +str(english_count)+'} to buffer::' +buffer_es.strip())        
                        queries.add(buffer_es.strip())
                        
        return queries

    def _affiliation_split(self, affiliation):
        phrases_list = []
        affiliation_tuple = re.subn('\(', ',', affiliation)
        affiliation = affiliation_tuple[0]
        affiliation_tuple = re.subn('\)', '', affiliation)
        affiliation = affiliation_tuple[0]
        comma_list = affiliation.split(',')
        for phrase in comma_list:
            phrases_list.append(phrase.strip())
        return phrases_list      


class Team:
    def __init__ (self, authors_list, affiliation_set, affiliation_string = ''):
        self.affiliation = affiliation_set
        self.members = authors_list
        self.affiliation_string = affiliation_string 




if __name__ == '__main__':
    main()
