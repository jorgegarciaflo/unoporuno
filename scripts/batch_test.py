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
#

from unoporuno.buscador import BuscadorDiasporas, ErrorBuscador

def main():
    buscador = BuscadorDiasporas()
    #TODO: leer los 23 según el nuevo formato batch
    # 
    name = 'Maria Villamil'
    topics = 'Potential Miscanthus Adoption in Illinois: Information Needs and Preferred Information Channels; Crop Sciences'
    #las organizaciones se separan con ;
    orgs = 'College of Agricultural, Consumer, and Environmental Sciences; University of Illinois at Urbana-Champaign'
    places = 'Illinois, Urbana-Champaign'
    resultado = buscador.genera_busquedas(name, topics, orgs, places)
    print 'total de snippets encontrados=', str(resultado.total)
    resultado.filtra_nominal(name)
    resultado.filtra_tematico(topics)

    # ordenado = resultado.seleccion()
    # ordenado = resultado.conjunto_resultante
    # if len(ordenado)>0:
    #     for s in reversed(ordenado):
    #         print '--------------------------------'
    #         print '|SNIPPET_TITLE::', s.title
    #         print '|SNIPPET_DESCRIPTION::', s.description
    #         print '|SNIPPET_LINK::', s.link
    #         print '|SNIPPET:ESA SCORE::', str(s.filter_status.semantic)
    #         print '---------------------------------'

    if len(resultado.conjunto_resultante)>0:
        ordenado = resultado.ordena_conjunto_resultante('query')
        for s in ordenado:
            print '--------------------------------'
            print '|SNIPPET_QUERY::', s.query
            print '|SNIPPET_TITLE::', s.title
            print '|SNIPPET_DESCRIPTION::', s.description
            print '|SNIPPET_LINK::', s.link
            print '|SNIPPET:ESA SCORE::', str(s.filter_status.semantic)
            print '---------------------------------'
        print '>>>>> ' +str(len(ordenado))+ '<<<<< RESULTING SNIPPETS'

if __name__ == "__main__":
    main()
