# -*- coding: utf8 -*-
#      This program is part of CIDESAL.incubator.iteration 1
__author__="Jorge García Flores"
__date__ ="$03-abr-2011 10:05:30$"

import sys

from xgoogle_unoporuno.search import GoogleSearch, SearchError

print 'hola mundo'

gs = GoogleSearch(sys.argv[1], True, False, 'fr')
gs.results_per_page = 10
results = gs.get_results()
for r in results:
    titulo = r.title.encode('utf-8')
    descripcion = r.desc.encode('utf-8')
    url = r.url.encode('utf-8')
    print '--------'
    print 'TITLE:', titulo
    print 'DESC:', descripcion
    print 'URL:', url
    
