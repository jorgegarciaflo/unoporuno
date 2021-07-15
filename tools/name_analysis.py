#/usr/bin/env python3
# -*- coding: utf-8 -*-
##
## Copyright (c) 2010-2021 Jessica López Espejel, Jorge J. García Flores, LIPN/CNRS/USPN

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
# usage: python3 name_analysis.py 'Miguel de la Madrid'

import sys
import nltk

def main():
    print("Name Analysis starting!")


class NameParser:
## Gramática descrita en (Garcia Flores et al. 2012)
## NC = nombre completo (PersonName en el paper)
## N = nombre (FirstName)
## A = apellido (LastName)
## I = inicial (Initial)
## AA = Nombre propio (Common Name)
## AG = Apellido o nombre con guión (TypoName)
## AD = partícula [ejemplos de, von, la] (ParticleName)
    
    def __init__(self):
        self.grammar_head = """
    NC -> N A
    N -> N I
    N -> N AA
    N -> I
    N -> AA
    N -> AG
    N -> AA AD
    A -> AAA
    A -> AAA AA
    A -> AAA AD
    A -> AAA AG
    A -> AAA I
    AAA -> AA
    AAA -> AG
    AAA -> AD
    """
        self.name_tokenizer_regex = r'(Mc[A-Z][a-z]+|O\'[A-Z][a-z]+|[Dd]e\s[Ll]a\s[A-Z][a-z]+|-[Dd]e-[A-Z][a-z]+|[A-Z][a-z]+-[A-Z][a-z]+|[Dd]e\s[Ll]a\s[A-Z][a-z]+|[Vv][oa]n\s[A-Z][a-z]+|[Dd]e[l]?\s[A-Z][a-z]+|[A-Z][\.\s]{1,1}|[A-Z][a-z]+|[Dd]e\s[Ll]os\s[A-Z][a-z]+)'    

        self.regexp_tagger_list = [(r'([A-Z][a-z]+-[A-Z][a-z]+|-[Dd]e-[A-Z][a-z]+)', 'AG'),
         (r'[A-Z][a-z]+', 'AA'),
         (r'[A-Z][\.\s]{1,1}', 'I'),                                   
         (r'([A-Z][a-z]+-[A-Z][a-z]+|[Dd]e\s[Ll]a\s[A-Z][a-z]+|[Vv][oa]n\s[A-Z][a-z]+|[Dd]e[l]?\s[A-Z][a-z]+|[Dd]e\s[Ll]os\s[A-Z][a-z]+)', 'AD'),
         (r'(Mc[A-Z][a-z]+|O\'[A-Z][a-z]+)', 'AA')]

        self.tokenizer = nltk.RegexpTokenizer(self.name_tokenizer_regex)
        self.tagger = nltk.RegexpTagger(self.regexp_tagger_list)

    def parse(self, name):
        tokens = self.tokenizer.tokenize(name)
        tag_tokens = self.tagger.tag(tokens)
        terminals = ''
        for ts in tag_tokens:
            terminals += ts[1] + " -> " + "'" + ts[0] + "'" + "\n    "
        grammar_rules = self.grammar_head + terminals
        grammar = nltk.parse_cfg(grammar_rules)
        parser = nltk.ChartParser(grammar)
        return parser.nbest_parse(tokens)        

    
if __name__=="__main__":
    main()


