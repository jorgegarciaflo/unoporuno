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
#      This program is part of CIDESAL.incubator.iteration 1
#
#      The goal of this class is to implement training features for snippets classification
#
# Features:
#           --regex: check if any regexp from a regexp list applies to a text
#           --gazeteer: checks if any word from a words list is in a text
__author__="Jorge García Flores"
__date__ ="$03-oct-2011 10:05:30$"

import re, logging, sys, time

"""
TODO: ignore blank lines from .gazt and .regex files
TODO: ignore \t\t\b\b separators
TODO: all features inherit from a feature object
class Feature(object):
    def __init__(self):
        self.exit_at_first = True
        self.hits = 0
"""

class RegexFeature(object):
    def __init__(self, unoporuno_root, regex_type):
        self.exit_at_first = True
        logging.basicConfig(level=logging.DEBUG)
        if not unoporuno_root in sys.path:
            sys.path.append(unoporuno_root + '/module/')
        from dospordos.tools import Limpieza
        self.limpieza = Limpieza()
        self.compiled_regex_list = []
        if regex_type=='organization':
            regex_file_path = unoporuno_root + '/resources/regex/organization.regex'
        elif regex_type=='biographical phrases':
            regex_file_path = unoporuno_root + '/resources/regex/biographical.phrases.regex'
        elif regex_type=='profession':
            regex_file_path = unoporuno_root + '/resources/regex/profession.regex'
        elif regex_type=='degree':
            regex_file_path = unoporuno_root + '/resources/regex/degree.regex'
        elif regex_type=='cv general':
            regex_file_path = unoporuno_root + '/resources/regex/cv.regex'
        elif regex_type=='cv http':
            regex_file_path = unoporuno_root + '/resources/regex/cv.http.regex'
        elif regex_type=='latin nationalities':
            regex_file_path = unoporuno_root + '/resources/regex/latin.american.nat.regex'
        elif regex_type=='world nationalities es':
            regex_file_path = unoporuno_root + '/resources/regex/world.nat.esp.regex'
        elif regex_type=='email':
            regex_file_path = unoporuno_root + '/resources/regex/email.regex'
        elif regex_type=='publication':
            regex_file_path = unoporuno_root + '/resources/regex/publication.regex'
        elif regex_type=='publication http':
            regex_file_path = unoporuno_root + '/resources/regex/publication.http.regex'
        elif regex_type=='thesis':
            regex_file_path = unoporuno_root + '/resources/regex/thesis.regex'
        elif regex_type=='thesis http':
            regex_file_path = unoporuno_root + '/resources/regex/thesis.http.regex'
        elif regex_type=='blacklist http':
            regex_file_path = unoporuno_root + '/resources/regex/blacklist.http.regex'
        else:
            raise FeatureError, 'Unrecognized regex feature type '+regex_type
        try:
            regex_file = open(regex_file_path, 'r')
        except:
            logging.error('Error opening regex resource file '+regex_file_path)
            raise FeatureError, 'Error opening regex resource file '+p_regex_file_path
        logging.info("Start loading gazetteer from " +regex_file_path+ " at " +time.asctime())
        for line in regex_file:
            if len(line.strip()) == 0:
                continue
            regex_line = line.split('\t')
            if len(regex_line) > 1:  
                case = regex_line[1].strip()
            else:
                case = 'cd'            
            #cd = case dependent
            #ci = case independent ==> re.IGNORECASE flag on
            regex = None
            if case == 'ci':
                regex = re.compile(regex_line[0].strip(), flags=re.IGNORECASE)
                logging.debug('compiling case independant regexp::' +regex_line[0].strip())
            else:
                regex = re.compile(regex_line[0].strip())
                logging.debug('compiling case dependant regexp::' +regex_line[0].strip())
            if regex:
                self.compiled_regex_list.append(regex)
        self.preposiciones = re.compile(" (at|of|de|del|do|for|in|für|da|der|des|degli|della|d')$")
        self.complemento = re.compile(" (at|of|de|del|do|for|in|für|da|der|des|degli|della|d')([A-Za-z ]+)")
        logging.info("End loading gazetteer from " +regex_file_path+ " at " +time.asctime())

    def test(self, line, exit_at_first=True):        
        clean_line = self.limpieza.limpia_acentos(line)
        #logging.debug('clean line = ' +clean_line)
        self.hits = 0
        regex_number = 0
        for r in self.compiled_regex_list:
            regex_number+=1
            result = r.search(clean_line)
            if result:
                self.hits += 1
                logging.debug('regex hit! exp. number ' +str(regex_number)+ ' in line ' +clean_line)
                if self.exit_at_first:
                    #logging.debug('exit at first!')
                    return self.hits
                    
        return self.hits
        
    def list_test(self, line):
        clean_line = self.limpieza.limpia_acentos(line)
        entity_list = []
        complemento = ''
        for r in self.compiled_regex_list:
            result = r.search(clean_line)
            if result:                
                #código específico para extraer las organizaciones que terminan en (at|of|de|del|do|for|in|für|da|der|des|degli|della|d')
                if self.preposiciones.search(result.group(0)):
                    re_complemento = self.complemento.search(clean_line)
                    if re_complemento:
                        complemento = re_complemento.group(2).rstrip()
                #sigue buscar y traer de cleanline todo lo que esté entre la preposición y un signo de puntuación
                logging.debug('regex hit! exp = ' +r.pattern+ ' in line ' +clean_line+ 'match='+ result.group(0)+ 'complement='+complemento)
                entity_list.append(result.group(0)+complemento)
        return entity_list

class GazetteerFeature(object):
    """
    ci = case independent
    cd = case dependent
    Para la búsqueda tipo cd sólo se necesita un set para buscar cada palabra upper.lower case en la lista
    Para la búsqueda de tipo ci se construye una regex para aislar la palabra con [ .,:;(<"¿]{1,1}palabra[ .,:;)>"?]{1,1}
    """
    def __init__(self, unoporuno_root, gazetteer_type, case_dependent=False):
        logging.basicConfig(level=logging.DEBUG)
        self.case_dependency = case_dependent
        self.exit_at_first = True
        if not unoporuno_root in sys.path:
            sys.path.append(unoporuno_root + '/module/')
        from dospordos.tools import Limpieza
        self.limpieza = Limpieza()
        self.compiled_regex = []
        
        if gazetteer_type=='country':
            gazetteer_file_path = unoporuno_root + '/resources/gazetteer/country.gazt'
        elif gazetteer_type=='city':
            if case_dependent:
                gazetteer_file_path = unoporuno_root + '/resources/gazetteer/world.cities.cd.gazt'
            else:
                gazetteer_file_path = unoporuno_root + '/resources/gazetteer/world.cities.ci.gazt'                
        elif gazetteer_type=='accronym':
            gazetteer_file_path = unoporuno_root + '/resources/gazetteer/accronyms.cd.gazt'
        elif gazetteer_type=='profession':
            gazetteer_file_path = unoporuno_root + '/resources/gazetteer/profession.ci.gazt'
        elif gazetteer_type=='degree':
            gazetteer_file_path = unoporuno_root + '/resources/gazetteer/degree.ci.gazt'
        elif gazetteer_type=='world nationalities en':
            gazetteer_file_path = unoporuno_root + '/resources/gazetteer/world.nat.eng.ci.gazt'
        else:
            raise GazetteerFeatureError, 'Unrecognized gazetteer feature type '+gazetteer_type
        try:
            gazetteer_file = open(gazetteer_file_path, 'r')
        except:
            logging.error('Error opening gazetteer resource file '+gazetteer_file_path)
            raise FeatureError, 'Error opening gazetteer resource file '+p_gazetteer_file_path

        logging.info("Start loading gazetteer list from " +gazetteer_file_path)
        
        for line in gazetteer_file:
            if len(line.strip()) == 0:
                continue            
            #logging.debug('adding ' +line+ ' to gazetteer.self.set')
            gazet_str = self.limpieza.limpia_reservados_regex(line.strip())
            if self.case_dependency:
                gazet_str = self.limpieza.limpia_acentos(gazet_str)
                #logging.debug (gazet_str+ ' added to case independant gazetter self set')
            else:
                gazet_str = self.limpieza.limpia_acentos(gazet_str).lower()
                #logging.debug (gazet_str+ ' added to case dependant gazetter self set')
            regex_str = '[ .\-,:;–(<"¿¡]{1,1}'+gazet_str+'[ .\-,:;)–>"?!]{1,1}'
            regex = re.compile(regex_str)
            if regex:
                self.compiled_regex.append((regex, gazet_str))
                
        logging.info("End loading gazetteer list from " +gazetteer_file_path)

    def test(self, line):
        clean_line = self.limpieza.limpia_acentos(line)
        #logging.debug('clean line = ' +clean_line)
        if self.case_dependency:
            for tupla in self.compiled_regex:
                result = tupla[0].search(clean_line)
                if result:
                    logging.debug('case independent gazetteer hit! ' +tupla[1]+ ' in line ' +line)
                    return True
            return False
        else:
            for tupla in self.compiled_regex:
                result = tupla[0].search(clean_line.lower())
                if result:
                    logging.debug('case independent gazetteer hit! ' +tupla[1]+ ' in line ' +line)
                    return True
            return False

    def entity_test(self, line):
        clean_line = self.limpieza.limpia_acentos(line)
        #logging.debug('clean line = ' +clean_line)
        if self.case_dependency:
            for tupla in self.compiled_regex:
                result = tupla[0].search(clean_line)
                if result:
                    logging.debug('case independent gazetteer hit! ' +tupla[1]+ ' in line ' +line)
                    return tupla[1]
            return ''
        else:
            for tupla in self.compiled_regex:
                result = tupla[0].search(clean_line.lower())
                if result:
                    logging.debug('case independent gazetteer hit! ' +tupla[1]+ ' in line ' +line)
                    return tupla[1]
            return ''

    def list_test(self, line):
        clean_line = self.limpieza.limpia_acentos(line)
        entity_list = []
        if self.case_dependency:
            for tupla in self.compiled_regex:
                result = tupla[0].search(clean_line)
                if result:
                    logging.debug('case independent gazetteer hit! ' +tupla[1]+ ' in line ' +line)
                    entity_list.append(tupla[1])
        else:
            for tupla in self.compiled_regex:
                result = tupla[0].search(clean_line.lower())
                if result:
                    logging.debug('case independent gazetteer hit! ' +tupla[1]+ ' in line ' +line)
                    entity_list.append(tupla[1].lower())
        return entity_list

class QualifiedGazetteerFeature(object):
    #a qualified gazetter file has the following structure:
    # expression \t type
    # expression is the item to search in the snippet
    #
    def __init__(self, unoporuno_root, gazetteer_type, case_dependent=False):
        logging.basicConfig(level=logging.DEBUG)
        self.case_dependency = case_dependent
        self.exit_at_first = True
        if not unoporuno_root in sys.path:
            sys.path.append(unoporuno_root + '/module/')
        from dospordos.tools import Limpieza
        self.limpieza = Limpieza()
        self.compiled_regex = []
        self.type_dict = dict()
        
        case = 'cd' if case_dependent else 'ci'
        if gazetteer_type=='country':
            gazetteer_file_path = unoporuno_root + '/resources/gazetteer/world.countries.'+case+'.gazt'
        elif gazetteer_type=='city':
            gazetteer_file_path = unoporuno_root + '/resources/gazetteer/world.cities.country.'+case+'.gazt'
        else:
            raise GazetteerFeatureError, 'Unrecognized gazetteer feature type '+gazetteer_type
        try:
            gazetteer_file = open(gazetteer_file_path, 'r')
        except:
            logging.error('Error opening gazetteer resource file '+gazetteer_file_path)
            raise FeatureError, 'Error opening gazetteer resource file '+gazetteer_file_path

        logging.info("Start loading gazetteer list from " +gazetteer_file_path)

        for line in gazetteer_file:
            line_n = line.strip()
            qualified_expression = re.split('\t',line_n)
            if len(line_n)==0 or len(qualified_expression)<2:
                continue
            gazet_str = self.limpieza.limpia_reservados_regex(qualified_expression[0])
            gazet_type = qualified_expression[1]            
            if self.case_dependency:
                gazet_str = self.limpieza.limpia_acentos(gazet_str)
                logging.debug (gazet_str+ ' of type ' +gazet_type+ ' added to case dependant gazetter self set')
            else:
                gazet_str = self.limpieza.limpia_acentos(gazet_str).lower()
                logging.debug (gazet_str+ ' of type ' +gazet_type+ ' added to case independant gazetter self set')
            #regex_str = '[ .\-,:;–(<"¿¡]{1,1}'+gazet_str+'[ .\-,:;)–>"?!]{1,1}'
            regex_str = '(^|[ .\-,:;–(<"¿¡]{1,1})'+gazet_str+'([ .\-,:;)–>"?!]{1,1}|$)'
            regex = re.compile(regex_str)
            if regex:
                self.compiled_regex.append((regex, gazet_str))
                d = dict({gazet_str:gazet_type})
                self.type_dict.update(d)
        logging.info("End loading gazetteer list from " +gazetteer_file_path)

    def test(self,line):
        clean_line = self.limpieza.limpia_acentos(line)
        #logging.debug('clean line = ' +clean_line)
        if self.case_dependency:
            for tupla in self.compiled_regex:
                result = tupla[0].search(clean_line)
                if result:
                    logging.debug('case dependent gazetteer hit! ' +tupla[1]+ ' in line ' +line)
                    return True
            return False
        else:
            for tupla in self.compiled_regex:
                result = tupla[0].search(clean_line.lower())
                if result:
                    logging.debug('case independent gazetteer hit! ' +tupla[1]+ ' in line ' +line)
                    return True
            return False

    def typed_test(self,line):
        clean_line = self.limpieza.limpia_acentos(line)
        if self.case_dependency:
            for tupla in self.compiled_regex:
                result = tupla[0].search(clean_line)
                if result:                    
                    if self.type_dict.has_key(tupla[1]):
                        tipo = self.type_dict[tupla[1]]                        
                        logging.debug('case dependent gazetteer hit! ' +tupla[1]+ ' of type:' +tipo+ ' in line ' +line)
                        return tipo.split(',')
                    else:
                        logging.debug('case dependent gazetteer hit! ' +tupla[1]+ ' of type: NOT FOUND in line ' +line)            
        else:
            for tupla in self.compiled_regex:
                result = tupla[0].search(clean_line.lower())
                if result:
                    if self.type_dict.has_key(tupla[1]):
                        tipo = self.type_dict[tupla[1]]
                        logging.debug('case independent gazetteer hit! ' +tupla[1]+ ' of type:' +tipo+ ' in line ' +line)
                        return tipo.split(',')
                    else:
                        logging.debug('case independent gazetteer hit! ' +tupla[1]+ ' of type: NOT FOUND in line ' +line)                  
        return ''

    def typed_list_test(self,line):
        clean_line = self.limpieza.limpia_acentos(line)
        type_set = set()
        if self.case_dependency:
            for tupla in self.compiled_regex:
                result = tupla[0].search(clean_line)
                if result:                    
                    if self.type_dict.has_key(tupla[1]):
                        tipo = self.type_dict[tupla[1]]
                        logging.debug('case dependent gazetteer hit! ' +tupla[1]+ ' of type:' +tipo+ ' in line ' +line)
                        type_set.update(tipo.split(','))
                    else:
                        logging.debug('case dependent gazetteer hit! ' +tupla[1]+ ' of type: NOT FOUND in line ' +line)
        else:
            for tupla in self.compiled_regex:
                result = tupla[0].search(clean_line.lower())
                if result:
                    if self.type_dict.has_key(tupla[1]):
                        tipo = self.type_dict[tupla[1]]
                        logging.debug('case independent gazetteer hit! ' +tupla[1]+ ' of type:' +tipo+ ' in line ' +line)
                        type_set.update(tipo.split(','))
                    else:
                        logging.debug('case independent gazetteer hit! ' +tupla[1]+ ' of type: NOT FOUND in line ' +line)                  
        return type_set


    def list_test(self,line):
        clean_line = self.limpieza.limpia_acentos(line)
        entity_list = []
        if self.case_dependency:
            for tupla in self.compiled_regex:
                result = tupla[0].findall(clean_line)
                if len(result)>0:
                    entity_list.append(tupla[1])
                    logging.debug('case dependent gazetteer hit! ' +tupla[0].pattern+ ' entities=' +str(result)+ ' in line ' +line)
        else:
            for tupla in self.compiled_regex:
                result = tupla[0].findall(clean_line.lower())
                if len(result)>0:
                    if self.type_dict.has_key(tupla[1]):
                        entity_list.append(tupla[1])
                        logging.debug('case dependent gazetteer hit! ' +tupla[0].pattern+ ' entities=' +str(result)+ ' in line ' +line)

        return entity_list


class FeatureError(Exception):
    pass
