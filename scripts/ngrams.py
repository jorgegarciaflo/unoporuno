#/usr/bin/env python
# -*- coding: utf8 -*-ç
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
# ngram freq calculator
# usage
#       python ngrams.py texto.txt ngram
#       python ngrams.py 4000_centros_investigacion.txt 2
import sys, nltk
from nltk.tokenize import PunktWordTokenizer

input_file = open(sys.argv[1])
s_ngrams = sys.argv[2]
input_ngrams = int(s_ngrams)
ngrams_in_text = []

for line in input_file:
    tokens = PunktWordTokenizer().tokenize(line)
    ngrams = nltk.ngrams(tokens, input_ngrams)
    ngrams_in_text += ngrams

# for line in input_file:
#     tokens = PunktWordTokenizer().tokenize(line)
#     bigrams  = nltk.bigrams(tokens)
#     bigrams_in_text += bigrams

frequency = nltk.FreqDist(ngrams_in_text)
for f in frequency:
    #print f
    ngram_str = ''
    for s in f:
        print s,
    print frequency[f]
