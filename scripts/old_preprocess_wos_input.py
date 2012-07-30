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
#      programmed by jorge.garcia-flores@limsi.fr on june 30 2011
# goal: select spanish name authors from a wos publications file and create a unoporuno friendly csv file
# usage:
# python preprocess_wos_input.py wos_file.txt > unoporuno_input.csv

__author__="Jorge García Flores"
__date__ ="$30-jun-2011 10:05:30$"

import sys, re, logging


UNOPORUNO_ROOT = '/home/harmodio/cidesal/code/unoporuno/'

def main():
    logging.basicConfig(level=logging.INFO)

    world = World()
    abbrev = Abbreviation()

    spanish_names = read_spanish_names(UNOPORUNO_ROOT)
    logging.debug ('spanish name list has ' +str(len(spanish_names)) +' names')
    wos_file = open(sys.argv[1])
    records = []
    record_limit = re.compile (r'\*Record [0-9]+ of [0-9]+\.')
    buffer = ''
    for wos_line in wos_file:
        if not (record_limit.search(wos_line)):
            buffer = buffer + wos_line
        else:
            records.append(buffer)
            buffer = ''
   
    logging.info('WOS records found in file:' +str(len(records)))
    if len(buffer)>0: records.append (buffer)
    re_title = re.compile(r'(Title:)\r?\n(.+)\r?\n')
    re_authors = re.compile(r'(Authors:)\r?\n(.+)\r?\n')
    re_authors_full_name = re.compile(r'(Author Full Names:)\r?\n(.+)\r?\n') 
    re_research_institution_address = re.compile(r'(Research Institution addresses:)\r?\n(.+)\r?\n')
    re_reprint_address = re.compile(r'(Reprint Address:)\r?\n(.+)\r?\n')

    publications = []
    publication_row = []
    for record in records:
        matches = [m.groups() for m in re_title.finditer(record)]
        for m in matches:
            publication_row.append(m[1].strip())
        matches = [m.groups() for m in re_authors.finditer(record)]
        for m in matches:
            publication_row.append(m[1].strip())
        matches = [m.groups() for m in re_authors_full_name.finditer(record)]
        for m in matches:
            publication_row.append(m[1].strip())    
        matches = [m.groups() for m in re_research_institution_address.finditer(record)]
        for m in matches:
            publication_row.append(m[1].strip())
        matches = [m.groups() for m in re_reprint_address.finditer(record)]
        for m in matches:
            publication_row.append(m[1].strip())    
        publications.append(publication_row)
        publication_row=[]
    logging.debug('Publications found: ' +str(len(publications)))

## ****** MAIN PUBLICATIONS LOOP ***********
    id = 1
    for publication_row in publications:
        if len(publication_row)>=4:
            title = publication_row[0]
            authors = publication_row[1]
            authors_full = publication_row[2]
            affiliation_string = publication_row[3]
            authors_list = wos_parse_authors_full_name(authors_full)
            logging.debug('Processing title:' +title)
            if len(authors_list)>1:
                 affiliation = Affiliation(affiliation_string, abbrev, world)
            else:
                if not re.search('\[', affiliation_string):
                    uni_aff = '[' + authors_full + ']' + affiliation_string
                    affiliation = Affiliation(uni_aff, abbrev, world)
                else:
                    affiliation = Affiliation(affiliation_string, abbrev, world)
            for team in affiliation.teams:
                spanish_authors_list=[]                
                for t in team.members:
                    if is_spanish_author(t, spanish_names):
                        logging.debug('Spanish author found! ' +t)
                        geo_list = []
                        orgs_list = []
                        for aff in team.affiliation:
                            if world.is_country(aff):
                                geo_list.append(aff)
                            elif world.is_city(aff):
                                geo_list.append(aff)
                            else:
                                orgs_list.append(aff)
                        orgs = ';'.join(orgs_list)
                        geo = ';'.join(geo_list)
                        logging.debug ('Name=' +t)
                        logging.debug('Organizations=' +orgs)
                        logging.debug('Geography=' +geo)
                        logging.debug('Topics=' +title)
                        print str(id)+ '|'  +t.strip()+ '|' +geo.strip()+ '|' +orgs.strip()+ '|' +title.strip()
                        id += 1

                        
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
    def __init__(self, countries=UNOPORUNO_ROOT+'resources/country_names.en.es.local.txt', cities=UNOPORUNO_ROOT+'resources/places.txt'):        
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

class Affiliation:
    def __init__(self, affiliation_string, abbv, world):
        self.teams = []
        self._affiliation_string = affiliation_string.strip()
        self._authors = []
        self._institutions=[]
        self._places = []
        #self._queries = []        
        self.parse_affiliation(abbv, self._affiliation_string)


    def parse_affiliation(self, abbv, new_affiliation_string = ''):
        if new_affiliation_string:
            self._affiliation_string = new_affiliation_string
        team_list = self._affiliation_string.split('[')
        for team in team_list:
            if team:
                affiliation_tuple = team.split(']')
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
                    lang = ''
                    self._queries = self._process_abbreviations(self._institutions, abbv, lang)
                    if self._authors and self._queries:
                        team = Team(self._authors, self._queries, self._affiliation_string)
                        self.teams.append(team)
                    #print 'Affiliation::self._authors', self._authors
                    #print 'Affiliation::self.institutions', self._institutions
                    #print 'Affiliation::self._queries', self._queries
               

    def _process_abbreviations(self, phrases, abv, lang):
        queries = set()
        for phrase in phrases:
            buffer_es = ''
            buffer_en = ''
            tokens = phrase.split()
            for token in tokens:
                if abv.abb_es.has_key(token):
                    buffer_es = buffer_es + ' ' + abv.abb_es[token]
                else:
                    buffer_es = buffer_es + ' ' + token
                if abv.abb_en.has_key(token):
                    buffer_en = buffer_en + ' ' + abv.abb_en[token]
                else:
                    buffer_en = buffer_en + ' ' + token
            if lang == 'en':
                queries.add(buffer_en.strip())
            elif lang == 'es':
                queries.add(buffer_es.strip())
            elif buffer_en == buffer_es:
            #if we don't know the language, we choose both
                queries.add(buffer_en.strip())
            else:
                if self.no_spanish_abv(abv, buffer_en):
                    queries.add(buffer_en.strip())
                if self.no_english_abv(abv, buffer_es):
                    queries.add(buffer_es.strip())
                
        return queries        

    def no_spanish_abv(self, abv, buffer):
        logging.debug('looking for spanish abv in:' +buffer)
        tokens = buffer.split()
        for token in tokens:
            if abv.abb_es.has_key(token):
                return False
        return True

    def no_english_abv(self, abv, buffer):
        logging.debug('looking for english abv in:' +buffer)
        tokens = buffer.split()
        for token in tokens:
            if abv.abb_en.has_key(token):
                return False
        return True

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
