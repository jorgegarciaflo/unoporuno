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
#      The goal is to read name, theme, organization and places of a person from
#       an XML file, to search its information in Google or Yahoo and to
#       filter the result snippets according to the following criteria:
#           : nominal: the snippet correspond to the possible variations of the person's name
#           : thematic: the snippet's topic correspond to the theme and organization topics
#           : biographic: the snippet's source document might containt biographica information \
#                about the person
#
#      USAGE python unoporuno.py <xml file> <resulting_snippets_file>
#
#      ALGORITHM:
#        1: read the snippet file
#        2: query the name and apply nominal, thematic and biographic filters
#        3: query the places and apply nominal, thematic and biographic filters
#        4: query the the themes and apply nominal, thematic and biographic filters
#
#     TODO:
#         a) Quitar el query del snippet para que no se repitan, salvo por la descripción o el título
#         b) Traducir los lugares geográficos
#         c) Implementar filtro semántico



__author__="Jorge García Flores"
__date__ ="$03-abr-2011 10:05:30$"

import sys, re, time, os, nltk
import ConfigParser, logging, time
import tempfile, libmorfo_python

import yql
from lxml import etree
from xgoogle_unoporuno.search import GoogleSearch, SearchError
from xgoogle_unoporuno.translate import LanguageDetector, DetectionError

UNO_ROOT = ''
FREELING_LIB = ''
FREELING_DATA = ''
RESEARCH_ESA = ''
#segundos que hay que dejar pasar entre dos consultas google
GOOGLE_WAIT = -1
OFFLINE = False
TOPIC_SEPARATOR = ';'
SNIPPETS_PER_QUERY = -1
DEFAULT_SEARCH_ENGINE = ''
YAHOO_APP_ID = ''


class BuscadorDiasporas(object):
    def __init__(self, nombre='', vinculo_buscado=''):
       global UNO_ROOT, FREELING_LIB, FREELING_DATA, RESEARCH_ESA, GOOGLE_WAIT, \
                OFFLINE, TOPIC_SEPARATOR, SNIPPETS_PER_QUERY, DEFAULT_SEARCH_ENGINE, \
                YAHOO_APP_ID
       self.creation_time = time.time()
       logging.basicConfig(level=logging.DEBUG)
       logging.info("main::Starting execution of unoporuno on " + time.asctime())
           

       config = ConfigParser.ConfigParser()
       config.read("unoporuno.conf")
       if len(config.sections())==0:
           logging.error("No configuration file on unoporuno.conf")
           exit(-1)
       try:
           UNO_ROOT = config.get('unoporuno', 'root')
           YAHOO_APP_ID = config.get('unoporuno', 'yahoo_app_id')
           google_wait_str = config.get('unoporuno', 'google_wait')
           offline_str = config.get('unoporuno', 'offline')
           snippets_per_query_str = config.get('unoporuno', 'snippets_per_query')    
           DEFAULT_SEARCH_ENGINE = config.get('unoporuno', 'default_search_engine')
           FREELING_LIB = config.get('freeling','lib')
           FREELING_DATA = config.get('freeling', 'data')
           RESEARCH_ESA = config.get('research-esa', 'root')        
       except ConfigParser.NoOptionError as e:
           logging.error('main::error: no value in unoporuno.conf configuration file, '\
                         +'section ' +e.section+ ', option ' +e.option)
           if e.option in ('google_wait', 'root', 'snipets_per_query', 'default_search_engine'):
               exit(-1)

       if google_wait_str:
           GOOGLE_WAIT = int(google_wait_str.strip())
       logging.info('main::GOOGLE_WAIT = ' +google_wait_str)
       logging.info('main::DEFAULT_SEARCH_ENGINE =' +DEFAULT_SEARCH_ENGINE)
       logging.info('main::SNIPPETS_PER_QUERY = ' +snippets_per_query_str)
       if YAHOO_APP_ID:
           logging.debug('main::YAHOO_APP_ID = ' +YAHOO_APP_ID)
       
       if offline_str == 'True':
           OFFLINE = True
           logging.info('main::ATTENTION... RUNNING OFFLINE!!!')
    
       if snippets_per_query_str:
           SNIPPETS_PER_QUERY = int(snippets_per_query_str.strip()) 
       
       if nombre:
           self.inicia(nombre)
           self._buscador = Buscador(nombre)

    def inicia(self, nombre, vinculo_buscado=''):
        self.creation_time = time.time()
        self._buscador = Buscador(nombre)
        if vinculo_buscado:
            self.__inicia_busquedas_vinculo(vinculo_buscado)
            self._resultados = ResultadoBusqueda(vinculo_buscado)
            self._resultados_parciales = ResultadoBusqueda(vinculo_buscado)       
        else:
            self.__inicia_busquedas_normales()
            self._resultados = ResultadoBusqueda()
            self._resultados_parciales = ResultadoBusqueda()

    def __inicia_busquedas_normales(self):
        self.genera_busquedas_nominales = self._genera_nominales_normal
        self.genera_busquedas_geograficas = self._genera_geograficas_normal
        self.genera_busquedas_organizacionales = self._genera_organizacionales_normal
        self.genera_busquedas_tematicas = self._genera_tematicas_normal

    def __inicia_busquedas_vinculo(self, vinculo):
        self.genera_busquedas_nominales = self._genera_nominales_vinculando
        self.genera_busquedas_geograficas = self._genera_geograficas_vinculando
        self.genera_busquedas_organizacionales = self._genera_organizacionales_vinculando
        self.genera_busquedas_tematicas = self._genera_tematicas_vinculando
        
    def genera_busquedas(self, temas, organizaciones, lugares):
        logging.info('unoporuno::busca::Generating queries for ' +self._buscador.nombre+ ',' +temas+ ',' +organizaciones+ ',' +lugares)

        #I variando nombre
        self.genera_busquedas_nominales()
        
        # #II variando geografía
        if lugares:
            self.genera_busquedas_geograficas(lugares)
                        
        # #III variando organizaciones
        if organizaciones:
            self.genera_busquedas_organizacionales(organizaciones)
        
        # #IV variando tema 
        if temas:
            self.genera_busquedas_tematicas(temas)
        
        return self._resultados

    def _genera_nominales_normal(self):
        self._resultados_parciales.renueva()
        try:
            snippets_res_en = self._consulta_web(self._buscador, 'en', '', '', 'name')
            snippets_res_es = self._consulta_web(self._buscador, 'es', '', '', 'name')
        except ErrorBuscador:
            raise ErrorBuscador
        self._resultados.almacena(snippets_res_en)
        self._resultados.almacena(snippets_res_es)        
        self._resultados_parciales.almacena(snippets_res_en)
        self._resultados_parciales.almacena(snippets_res_es)        
        return self._resultados_parciales

    def _genera_geograficas_normal(self, geo):
        self._resultados_parciales.renueva()
        lista_lugares = geo.split(TOPIC_SEPARATOR)
        # #TODO: traducir el nombre de los lugares
        for lugar in lista_lugares:            
            try:
                snippets_res_en = self._consulta_web(self._buscador, 'en', lugar, '', 'geo')
                snippets_res_es = self._consulta_web(self._buscador, 'es', lugar, '', 'geo')
            except ErrorBuscador:
                raise ErrorBuscador
            self._resultados_parciales.almacena(snippets_res_en)
            self._resultados_parciales.almacena(snippets_res_es)     
            self._resultados.almacena(snippets_res_en)
            self._resultados.almacena(snippets_res_es)
        return self._resultados_parciales

    def _genera_organizacionales_normal(self, orgs):
        self._resultados_parciales.renueva()
        consulta_organizaciones = Organizaciones().consulta_organizaciones
        lista_organizaciones = consulta_organizaciones(orgs)
        for query in lista_organizaciones:
            try:
                snippets_res = self._consulta_web(self._buscador, query.language, query.text, '', 'orgs')
            except ErrorBuscador:
                raise ErrorBuscador
            self._resultados_parciales.almacena(snippets_res)
            self._resultados.almacena(snippets_res)
        return self._resultados_parciales

    def _genera_tematicas_normal(self, temas):
        self._resultados_parciales.renueva()
        consulta_temas = Temas().consulta_temas
        lista_temas = consulta_temas(temas)
        for query in lista_temas:
            try:
                snippets_res = self._consulta_web(self._buscador, query.language, query.text, '', 'topics')
            except ErrorBuscador:
                raise ErrorBuscador
            self._resultados_parciales.almacena(snippets_res)
            self._resultados.almacena(snippets_res)
        return self._resultados_parciales
        

    def _genera_nominales_vinculando(self):
        self._resultados_parciales.renueva()
        variaciones_nominales = self._varia_nombre(self._buscador.nombre)
        for variacion in variaciones_nominales:            
            try:
                snippets_res_en = self._consulta_web(self._buscador, 'en', '', variacion, 'name')
                self._resultados.almacena(snippets_res_en)
                self._resultados_parciales.almacena(snippets_res_en)            
                if self._resultados_parciales.vinculo_encontrado:
                    return self._resultados_parciales
                snippets_res_es = self._consulta_web(self._buscador, 'es', '', variacion, 'name')
                self._resultados.almacena(snippets_res_es)        
                self._resultados_parciales.almacena(snippets_res_es)
                if self._resultados_parciales.vinculo_encontrado:
                    return self._resultados_parciales
            except ErrorBuscador:
                raise ErrorBuscador
        return self._resultados_parciales


    def _genera_geograficas_vinculando(self, geo):
        self._resultados_parciales.renueva()
        lista_lugares = geo.split(TOPIC_SEPARATOR)
        # #TODO: traducir el nombre de los lugares
        for lugar in lista_lugares:            
            try:
                snippets_res_en = self._consulta_web(self._buscador, 'en', lugar, '', 'geo')
                snippets_res_es = self._consulta_web(self._buscador, 'es', lugar, '', 'geo')
            except ErrorBuscador:
                raise ErrorBuscador
            self._resultados_parciales.almacena(snippets_res_en)
            self._resultados_parciales.almacena(snippets_res_es)     
            self._resultados.almacena(snippets_res_en)
            self._resultados.almacena(snippets_res_es)
        return self._resultados_parciales

    def _genera_organizacionales_vinculando(self, orgs):
        self._resultados_parciales.renueva()
        consulta_organizaciones = Organizaciones().consulta_organizaciones
        lista_organizaciones = consulta_organizaciones(orgs)
        for query in lista_organizaciones:
            try:
                snippets_res = self._consulta_web(self._buscador, query.language, query.text, '', 'orgs')
            except ErrorBuscador:
                raise ErrorBuscador
            self._resultados_parciales.almacena(snippets_res)
            self._resultados.almacena(snippets_res)
        return self._resultados_parciales

    def _genera_tematicas_vinculando(self, temas):
        self._resultados_parciales.renueva()
        consulta_temas = Temas().consulta_temas
        lista_temas = consulta_temas(temas)
        for query in lista_temas:
            try:
                snippets_res = self._consulta_web(self._buscador, query.language, query.text, '', 'topics')
            except ErrorBuscador:
                raise ErrorBuscador
            self._resultados_parciales.almacena(snippets_res)
            self._resultados.almacena(snippets_res)
        return self._resultados_parciales
        

    def _consulta_web(self, buscador, language, query='', variacion='', query_type=''):
        snippets_res = []        
        try:
            snippets_res = self._aplica_busqueda(buscador, language, query, variacion, query_type)
        except ErrorBuscador:
                raise ErrorBuscador
        return snippets_res

    #TODO sig_pag sólo para Google
    def _aplica_busqueda(self, buscador, language, query, variacion='', query_type=''):
        snippets = []
        if OFFLINE is True:
            snippets = self._offline_dummy_snippets(query.strip())
            return snippets
        try:
            snippets = buscador.busca(query.strip(), language, variacion, query_type)
            while 0< len(snippets)< SNIPPETS_PER_QUERY :
                new_snippets = buscador.busca_sig_pag()
                if len(new_snippets)>0:
                    snippets += new_snippets
                else:
                    break
                
            return snippets
        except SearchError:
            logging.error ("No research engine availiable: check your internet connextion!")
            raise ErrorBuscador, "No research engine availiable: check your internet connextion!"
    
    def _offline_dummy_snippets(self, query):
        snippets = []
        dummy_snippet = Snippet(query, 'offline dummy snippet 1', 'dummy description \
        blah blah blah', 'http://dummy.link.offline')
        snippets.append(dummy_snippet)
        return snippets

    def _varia_nombre(self, n):
    #TODO: variar con NameParser
        nombre = n.strip()
        result_list = []
        result_list.append(nombre)
        re_2_sin_inicial = re.match('^([A-Z][a-z]+) ([A-Z][a-z]+)$', nombre)
        re_3_con_inicial = re.match('^([A-Z][a-z]+) ([A-Z]) ([A-Z][a-z]+)$', nombre)
        if re_2_sin_inicial:
            variacion = re_2_sin_inicial.group(1) +' * '+ re_2_sin_inicial.group(2)
            logging.debug('main::varia_nombre: agregando variación nominal:' + variacion)
            result_list.append(variacion)
        elif re_3_con_inicial:
            variacion = re_3_con_inicial.group(1) +' '+ re_3_con_inicial.group(2) +'* '+ \
                        re_3_con_inicial.group(3)
            logging.debug('main::varia_nombre: agregando variación nominal:' + variacion)            
            result_list.append(variacion)
        return result_list
    
class ResultadoBusqueda(object):
    def __init__(self, vinculo_buscado=''):
        self.total_snippets = 0
        self.snippets = set([])
        self.total_queries = 0
        self.vinculo_encontrado = False
        limpieza = Limpieza()
        self._vinculo_buscado =  limpieza.limpia_reservados_xml(vinculo_buscado)
        
        if vinculo_buscado:
            self.almacena = self._almacena_buscando
        else:
            self.almacena = self._almacena_normal
        
    def _almacena_buscando(self, lista_snippets):
        if self.vinculo_encontrado:
            return
        self.total_queries += 1
        for s in lista_snippets:
            
            logging.debug('ResultadoBusqueda.almacenabuscando::comparing ' +s.link+ ' of length '+ str(len(s.link))+' WITH ' +self._vinculo_buscado+ ' of lenght ' +str(len(self._vinculo_buscado)))
            if s.link.strip() == self._vinculo_buscado.strip():
                self.vinculo_encontrado = True
                s.filter_status.vinculo_encontrado = True
                self.snippets.add(s)
                self.total_snippets += 1
                return                
            self.snippets.add(s)
            self.total_snippets += 1
                
                
    def _almacena_normal (self, lista_snippets):
        self.total_queries += 1
        for s in lista_snippets:
            self.snippets.add(s)
            self.total_snippets += 1

    def renueva(self):
        self.total_snippets = 0
        self.snippets = set([])
        self.total_queries = 0        
        self._vinculo_encontrado = False        
                
    def nominales(self):
        conjunto = set([])
        for s in self.snippets:
            if s.filter_status.nominal is True:
                conjunto.add(s)
        return conjunto

    def tematicos(self):
        conjunto = set([])
        for s in self.snippets:
            if s.filter_status.semantic > 0:
                conjunto.add(s)
        if len(conjunto)>0:
            return sorted(conjunto, key=lambda snippet: snippet.filter_status.semantic)
    
        return conjunto

    def biograficos(self):
        #TODO
        return set([])

    def seleccion(self):
        conjunto = set([])
        for s in self.snippets:
            if s.filter_status.nominal is True and s.filter_status.semantic > 0:
                conjunto.add(s)
        if len(conjunto)>0:
            return sorted(conjunto, key=lambda snippet: snippet.filter_status.semantic)
        else:
            return conjunto

    def ordena_snippets (self, snippet_field = 'query'):
        #TODO: hacer los campos no textuales
        if snippet_field == 'query':
            return sorted(self.snippets, key=lambda snippet: snippet.query)
        elif snippet_field == 'title':
            return sorted(self.snippets, key=lambda snippet: snippet.title)
        elif snippet_field == 'link':
            return sorted(self.snippets, key=lambda snippet: snippet.title)
        elif snippet_field == 'filter_status.semantic':
            return sorted(self.snippets, key=lambda snippet: snippet.filter_status.semantic)
        #TODO: snippet.filter_status.biographic ¿es numérico o binario?
        
        
    def filtra_nominal(self, nombre):
        filtra = Filtro(list(self.snippets))
        lista_resultante = filtra.nominal(nombre)
        if len(lista_resultante) == len(self.snippets):
            self.snippets = set(lista_resultante)
        return lista_resultante

    def filtra_tematico(self, tema):
        filtra = Filtro(list(self.snippets))
        lista_resultante = filtra.tematico(tema)
        if len(lista_resultante) == len(self.snippets):
            self.snippets = set(lista_resultante)
        return lista_resultante

    def filtra_biografico(self, lengua):
        return list(self.snippets)        
    
class GeneradorBusquedas:
    def __init__(self, buscador, tipo, busqueda_str):
        self.buscador = buscador
        self.tipo = tipo
        self.busqueda_original = busqueda_str
        self.detalle_busquedas = [] #lista de string con las búsquedas individuales
        self.resultado_snippets = []   #lista de snippets con el resultado de todas las búsquedas 

        if self.tipo == 'geo':
            self.detalle_busquedas = self.parse_geo_query(self.busqueda_original)

    #esta función separa simplemente por comas el string de lugares
    def parse_geo_query(self, query_string):
        queries = query_string.split(',')
        return queries

    def busca(self):
        for q in self.detalle_busquedas:
            self.buscador.busca(q.strip())
            self.resultado_snippets = self.resultado_snippets + self.buscador.snippets
        
        return self.buscador.snippets

#buscador de personas, le agrega el nombre a todas las búsquedas
#si a Buscador.busca() no se le pasa parámetro, busca con el puro nombre
#importante: name.title() // si no, la gramática de nominal filter no jala
class Buscador:
    def __init__(self, name):
        global GOOGLE_WAIT, DEFAULT_SEARCH_ENGINE, YAHOO_APP_ID, SNIPPETS_PER_QUERY
        self.nombre = name.title()
        self.snippets = []
        self.consulta = ''
        self.lengua = ''
        self.last_query_time = time.mktime( (1972,1,4,0,0,0,0,0,0) )
        self._espera = GOOGLE_WAIT
        self._gs = None
        self._ys = None
        self.default_search_engine = DEFAULT_SEARCH_ENGINE
        self.snippets_per_query = SNIPPETS_PER_QUERY
        self.yahoo_app_id = YAHOO_APP_ID
        if self.default_search_engine == 'google':
            self.busca = self._g_busca
            self.busca_sig_pag = self._g_busca_sig_pag
        elif self.default_search_engine == 'yahoo':
            self.busca = self._y_busca
            self.busca_sig_pag = self._y_busca_sig_pag
        
    def _g_busca(self, query = '', lengua='en', nombre_alterado = '', query_type=''):
        self.query_type = query_type
        if nombre_alterado:
            self.consulta = nombre_alterado.title() + ' ' + query
        else:
            self.consulta = self.nombre + ' ' + query
        self.lengua = lengua
        self.snippets = []
        wait = time.time() - self.last_query_time
        logging.debug('Buscador::start waiting google at ' + time.ctime(time.time()))
        while wait < self._espera:
            wait = time.time() - self.last_query_time
            if wait < 0:
                logging.error('Time error waiting for google')
                break
        logging.info('Buscador::end waiting google at ' + time.ctime(time.time()))
        try:
            logging.info('Buscador::searching for ' +self.consulta+ '; language=' +self.lengua)
            self._gs = GoogleSearch(self.consulta,True,False,self.lengua)
            self._gs.results_per_page = 10
            results = self._gs.get_results()
            self.last_query_time = time.time()
            logging.info('busca::querying ' + self.consulta + ' last_query_time:: ' + \
                          time.ctime(self.last_query_time))
            for r in results:
                titulo = r.title.encode('utf8')
                descripcion = r.desc.encode('utf8'
                #logging.debug('Buscador::DESCRIPTION_BUG::_g_busca::descripcion='+descripcion) 12/OCT/2012
                url = r.url.encode('utf8')
                r_snippet = Snippet(self.consulta, titulo,
                                    descripcion, url, 'google', self.query_type)
                self.snippets.append(r_snippet)
            logging.debug('busca::<< ' + str(len(results)) + ' >> resulting snippets')
            return self.snippets
        except SearchError, e:
            #todo raise an error and put all filed google queries in a queue to latar processing
            logging.error ("Search failed: %s")
            raise SearchError, e
    #TODO: raise an error if no browser or no connexion

    def _g_busca_sig_pag(self):
        ret_snippets = []
        wait = time.time() - self.last_query_time
        logging.debug('Buscador::start waiting google at ' + time.ctime(time.time()))
        while wait < self._espera:
            wait = time.time() - self.last_query_time
            if wait < 0:
                logging.error('Time error waiting for google')
                break
        logging.info('Buscador::end waiting google at ' + time.ctime(time.time()))
        try:
            logging.info('Buscador::searching next page for ' +self.consulta+ '; language=' +self.lengua)
            results = self._gs.get_results()
            self.last_query_time = time.time()
            for r in results:
                titulo = r.title.encode('utf8')
                descripcion = r.desc.encode('utf8')
                url = r.url.encode('utf8')
                r_snippet = Snippet(self.consulta, titulo, descripcion,
                                    url, 'google', self.query_type)
                ret_snippets.append(r_snippet)
                self.snippets.append(r_snippet)
            logging.debug('busca::<< ' + str(len(results)) + ' >> resulting snippets')
            return ret_snippets
        except SearchError, e:
            #todo raise an error and put all filed google queries in a queue to latar processing
            logging.error ("Search failed: %s")
            raise SearchError, e
    #TODO: raise an error if no browser or no connexion

    def _y_busca(self, query = '', lengua='en', nombre_alterado = '', query_type=''):

        
        ret_snippets = []
        if nombre_alterado:
            self.consulta = nombre_alterado + ' ' + query
        else:
            self.consulta = self.nombre + ' ' + query
        self.lengua = lengua
        self.snippets = []
        wait = time.time() - self.last_query_time
        logging.debug('Buscador::wait= ' +str(wait)+ ' self._espera= ' +str(self._espera) )
        logging.debug('Buscador::start waiting yahoo at ' + time.ctime(time.time()))
        while wait < self._espera:
            wait = time.time() - self.last_query_time
            if wait < 0:
                logging.error('Time error waiting for yahoo')
                break
        logging.info('Buscador::end waiting yahoo at ' + time.ctime(time.time()))
        self._ys = yql.Public()
        yql_query = 'select * from search.web(0,'+str(self.snippets_per_query)+\
                    ') where query="'+self.consulta+'" and appid="'+\
                    self.yahoo_app_id+'"'
        logging.debug('Buscador::_y_busca:yql_query = ' +yql_query)
        result = self._ys.execute(yql_query)
        self.last_query_time = time.time()
        for row in result.rows:
            u_titulo = row['title']
            u_descripcion = row['abstract']
            u_url = row['clickurl']
            titulo = ''
            descripcion = ''
            url = ''
            if u_titulo:
                titulo = u_titulo.encode('utf-8')
            if u_descripcion:
                descripcion = u_descripcion.encode('utf-8')
            if u_url:
                raw_url = u_url.encode('utf-8')
            url_split = raw_url.split('http%3A')
            if len(url_split)>1:
                url = 'http:' + url_split[1]
            else:
                url = raw_url
            r_snippet = Snippet(self.consulta, titulo, descripcion,
                                url, 'yahoo', query_type)
            self.snippets.append(r_snippet)
        logging.debug('busca::<< ' + str(len(result.rows)) + ' >> resulting snippets')
        return self.snippets
        
        """
    TODO: ADD TRY, EXCEPT not to stop the whole program
        except:
            logging.error("Yahoo search failed")
            raise ErrorBuscador
        """
        return self.snippets

    #TODO sigpag sólo para google. 
    def _y_busca_sig_pag(self):
        return self.snippets

class Snippet:
    def __init__(self, query, title, description, link, engine='google', query_type='std'):
        #TODO: quitarle el query, para que no haya repeticiones
        self.query = query
        self.query_type = query_type
        self.title = title.strip()
        self.description = description.strip()
        #logging.debug('snippet::DESCRIPTION_BUG::description='+self.description)
        self.description.replace('\n','§')
        if self.title != self.description:
            self.string = self.title + ' § ' + self.description
        else:
            self.string = self.title
        self.link = link
        self.engine = engine
        self.filter_status = FilterStatus()
        logging.debug('snippet::creating snippet: ' + self.string)
        
class Query:
    def __init__ ( self, q, l='en', t = ''):
        self.type = t
        self.text = q
        self.language = l

class ErrorBuscador(Exception):
    pass
    #base class for errors of unoporuno


class Persona:
    #TODO: hacer que persona herede de lista y poder iterar sobre ella
    #      por el momento nos conformamos con un sólo registro
    def __init__(self, input_xml):
        try:
            self.arbol = etree.parse(input_xml)
        except etree.XMLSyntaxError:
            logging.error('invalid xml input file:' + input_xml)
        self.raiz = self.arbol.getroot()
        logging.debug('Persona::root tag = ' + self.raiz.tag)

    def nombre(self):        
        nombre = self.raiz.find(".//name")
        retstr = self._tostring(nombre)
        return retstr

    def temas(self):
        tema = self.raiz.find(".//topics")
        retstr = self._tostring(tema)
        return retstr
        
    def organizaciones(self):        
        organizacion= self.raiz.find(".//organizations")
        retstr = self._tostring(organizacion)
        return retstr
        
    def lugares(self):
        lugar = self.raiz.find(".//places")
        retstr = self._tostring(lugar)
        return retstr
        
    def _tostring(self, elemento):
        if elemento is not None:
            return_str = re.sub('\r?\n[ \t]*', ' ' , elemento.text.strip())
            return return_str
        else:
            return ''

class FilterStatus:
    def __init__(self):
        self.nominal = False
        self.semantic = 0.000
        self.biographic = False
        self.vinculo_encontrado = False
        

class Filtro:
    def __init__(self, lista):
        self.snippets = lista
        self.seleccion = set([])
                
    def nominal(self, nombre):
        self._filtro_nominal = FiltroNominal(nombre)
        for s in self.snippets:
            if self._filtro_nominal.filtra(s.string):
                s.filter_status.nominal = True
        return self.snippets

    def tematico(self, tema):
        self._filtro_semantico = FiltroSemantico(tema)
        for s in self.snippets:
        #self._filtro_semantico.filtra regresa un float
            s.filter_status.semantic = self._filtro_semantico.filtra(s.string)
        return self.snippets
        

    def biografico(self):
        return self.snippets

    def selecciona(self):
        
        for s in self.snippets:
            if s.filter_status.nominal is True and s.filter_status.semantic > 0.0 :
                logging.debug('main::valid nominal and semantic snippets:' + s.string)
                logging.debug('main::semantic score=' + str(s.filter_status.semantic))
                self.seleccion.add(s)
        for s in self.snippets:
            if s.filter_status.nominal is True:
                logging.debug('main::valid nominal snippets:' + s.string)
        for s in self.snippets:
            if s.filter_status.semantic > 0:
                logging.debug('main::valid semantic snippets:' + s.string)
        return self.seleccion

class FiltroSemantico:
    def __init__(self, tema):
        self._tema = tema
        
    def filtra(self, snippet_str):
        #Better for security delete = False
        #self._tmp_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_file = tempfile.NamedTemporaryFile()
        snippet_str = self._limpia_esa(snippet_str)
        #para el CGI esto no jala
        command = UNO_ROOT + '/scripts/calculate_esa.sh "' + self._tema + '" "' + \
                  snippet_str + '" > ' + tmp_file.name + " 2>&1"
        #from a CGI we need to run calculate_esa from cgi-bin, and maybe the whole jar
        #command = 'calculate_esa.sh "' + self._tema + '" "' + \
        #                         snippet_str + '" > ' + tmp_file.name + " 2>&1"
        logging.debug('FiltroSemantico::semantic relatedness command:' + command)
        os.system(command)
        logging.info('CALCULATING SEMANTIC RELATEDNESS OF ' +self._tema+ ' AGAINST:' +snippet_str)
        for line in tmp_file:
            logging.debug('FiltroSemantico::reading line ' + line)
            if re.search('ESA Similarity:', line):
                score_re = re.search('[01][,\.][0-9]+', line)
                if score_re:
                    score_str = score_re.group(0)
                    score_str = score_str.replace(',', '.')
                    logging.info ('FiltroSemantico::semantic relatedness=' + score_str)
                    score = float(score_str)
                    tmp_file.close()
                    return score
        tmp_file.close()
        return 0.0

    #Función aberrante que baja a minúsculas y quita todos los signos de puntuación
    #para que research_esa lo pueda evaluar
    def _limpia_esa(self, esa_str):
        res_str = esa_str.lower()
        res_str = re.subn('[,\.:;]',' ', res_str)[0]
        res_str = res_str.replace('"', '')
        return res_str
                    



# ESTA CLASE REPRODUCE LAS FUNCIONES DE nominal_coref.py
class FiltroNominal:
    def __init__(self, name):
        nombre = self._separa_iniciales(name)
        nombre = nombre.title()
        logging.debug('Starting FiltroNominal class for ' +nombre)
        self._name_parser = NameParser()
        self._trees = self._name_parser.parse(nombre)
        self._regex_list = self._name_variations (nombre, self._trees)
        self._limpieza = Limpieza()
        

    def _name_variations(self, name, trees):
        variations = []
        for tree in trees:
            if len(tree)<2:
                return variations
            
            name_text = name.strip()
            nombre = tree[0]
            apellido = tree[1]
            #literal nombre, literal apellido
            s=self._literal(nombre)
            l=self._literal(apellido)
            #variations.append(name_text)
            variations = self._add_variation(s,l,variations,'LnLa')
            #literal apellido, literal nombre
            variations = self._add_variation(l,s,variations,'LaLn', ',? +')
            #literal sin inicial
            s=self._sin_inicial(nombre)
            l=self._sin_inicial(apellido)
            variations = self._add_variation(s,l,variations,'SInSIa')
            #EXPANDE(nombre) PRINT(apellido) 
            s=self._expande(nombre)
            l=self._literal(apellido)
            variations = self._add_variation(s,l,variations, 'EnLa')
            variations = self._add_variation(l,s,variations, 'LaEn', ',? +')
            #CONTR(nombre) PRINT(apellido)
            s=self._contrae(nombre)
            variations = self._add_variation(s,l,variations, 'CnLa')
            variations = self._add_variation(l,s,variations, 'LaCn', ',? +')
            #PRINT(nombre) CONTRAE(apellido)
            #logging.debug('****ANTES DE >>>> CaLn, len(nombre)=' +str(len(nombre))+ ', len(apellido)=' +str(len(apellido)))
            l=self._literal(nombre)
            s=self._contrae(apellido)
            variations = self._add_variation(l,s,variations, 'LnCa')
            variations = self._add_variation(s,l,variations, 'CaLn', ',? +')
            #PRINT(nombre) EXPANDE(apellido) 
            s = self._expande(apellido)
            variations = self._add_variation(l,s,variations, 'LnEa')
            variations = self._add_variation(s,l,variations, 'EaLn', ',? +')
            #CONTR(nombre) CONTRAE(apellido)
            #logging.debug('antes de CnCa, len(nombre)=' +str(len(nombre))+ ', len(apellido)=' +str(len(apellido)))
            l = self._contrae(nombre)
            s = self._contrae(apellido)
            variations = self._add_variation(l,s,variations, 'CnCa')
            variations = self._add_variation(s,l,variations, 'CaCn', ',? +')
            #EXP(nombre) EXPANDE(apellido) 8
            l = self._expande(nombre)
            s = self._expande(apellido)
            variations = self._add_variation(l,s,variations, 'EnEa')
            variations = self._add_variation(s,l,variations, 'EaEn', ',? +')
            #EXP(nombre) CONTRAE(apellido) 9
            
            l = self._expande(nombre)
            s = self._contrae(apellido)
            variations = self._add_variation(l,s,variations, 'EnCa')
            variations = self._add_variation(s,l,variations, 'CaEn', ',? +')
            #CONTR(nombre) EXP(apellido) 10
            l = self._contrae(nombre)
            s = self._expande(apellido)
            variations = self._add_variation(l,s,variations, 'CnEa')
            variations = self._add_variation(s,l,variations, 'EaCn', ',? +')
            if len(nombre)>=1 and len(apellido)>=1:
                #PRINT(nombre) [inicial] #PRINT(apellido) 11
                #logging.debug('antes de LnILa, len(nombre)=' +str(len(nombre))+ ', len(apellido)=' +str(len(apellido)))
                l = self._literal(nombre) 
                s = self._literal(apellido)
                variations = self._add_variation(l,s,variations,'LnILa', ' [A-Z][\.]? ')
                #PRINT(nombre) [nombre/apodo] #PRINT(apellido) 12
                #logging.debug('antes de LnXLa, len(nombre)=' +str(len(nombre))+ ', len(apellido)=' +str(len(apellido)))
                l = self._literal(nombre)
                s = self._literal(apellido) 
                variations = self._add_variation(l,s,variations, 'LnXLa', ',?[- ]+[A-Z][a-z]+ ')
                variations = self._add_variation(s,l,variations, 'LaXLn', ',?[- ]+[A-Z][a-z]+ ')

            #PRIMER(nombre) #PRIMER(apellido)
            l = self._literal(nombre[0])
            s = self._literal(apellido[0])
            variations = self._add_variation(l,s,variations, 'Ln0La0')
             
            logging.debug('****ANTES DE >>>> Ln0Cn1La, Ln0Cn1La0Ca1 len(nombre)=' +str(len(nombre))+ ', len(apellido)=' +str(len(apellido)))
            if len(nombre)>1:
                if nombre[0].node!='I':
                #PRIMER(nombre) LITERAL(apellido):
                    l = self._literal(nombre[0])
                    s = self._literal(apellido)
                    variations = self._add_variation(l,s,variations, 'Ln0La')
                    if len(apellido)>1:
                #SEGUNDO(nombre) #PRIMER(apellido)
                        l = self._literal(nombre[1])
                        s = self._literal(apellido[0])
                        variations = self._add_variation(l,s,variations, 'Ln1La0')
                #DOS APELLIDOS CON GUION
                        l = self._literal(apellido[0])
                        s = self._literal(apellido[1])
                        variations = self._add_variation(l,s,variations, 'La0-La1', '')
                if nombre[1].node!='I':
        #PRIMER(nombre) #CONTRAE(SEGUNDO(nombre)) #LITERAL(apellido)
                    l = self._literal(nombre[0])
                    m = self._contrae(nombre[1])
                    s = self._literal(apellido)
                    n = l + m
                    variations = self._add_variation(n,s,variations,'Ln0Cn1La')
                    if len(apellido)>1:
        #PRIMER(nombre) #CONTRAE(SEGUNDO(nombre)) #PRIMER(apellido) #CONTRAE(2oapellido) 
                        o = self._literal(apellido[0])
                        p = self._contrae(apellido[1])
                        q = o + ' ' + p
                        variations = self._add_variation(n, q,variations,'Ln0Cn1La0Ca1')
                
                    
        return variations

    def _add_variation(self, s, l, var_list, tipo='N/A', separador=' '):
        if s and l:
            variante = s.strip() + separador + l.strip()
            if variante.endswith('[ \-]+'):
                variante = variante.rstrip('[ \-]+')
            if variante.endswith('[ -]+'):
                variante = variante.rstrip('[ -]?')
            if variante not in var_list:
                var_list.append(variante)
                logging.debug ('FiltroNominal::adding variation ' +variante+ ' of type ' +tipo)
        return var_list

    def _expande(self, tree):
        if len(tree.pos()) > 1:
            name_buffer = ''
            for rama in tree:
                name_buffer += self._expande(rama) + ' '
            return name_buffer.strip()
        else:
            tuple = tree.pos()[0]
            if tuple[1]=='I':
                expansion = re.sub(r'[\.\s]', '[a-z]+', tuple[0])
                return expansion
            else:
                return tuple[0]

    def _contrae(self, tree):
        #logging.debug( 'contrayendo::tree' +str(tree))
        #logging.debug( 'contrayendo::tree.node' +str(tree.node))
        if len(tree.pos()) > 1:
            name_buffer = ''
            for rama in tree:
                name_buffer += self._contrae(rama) + '[ -]?'
                #logging.debug ('contrayendo::name_buffer=' +name_buffer)
            return name_buffer.strip()
        else:
            contraccion = ''
            tuple = tree.pos()[0]
            #logging.debug( 'contrayendo::height' +str(tree.height()))
            #verificando si es un primer apellido incompresible
            if tree.node == 'AAA':
                return self._contrae_1er_apellido(tuple[0])
            elif type(tree[0]) == nltk.tree.Tree:
                if tree[0].node == 'AAA':
                    return self._contrae_1er_apellido(tuple[0])
            #logging.debug( 'contrayendo::tuple' +str(tuple))
            if tuple[1]=='AA' and tuple[0][0].istitle():
                contraccion = tuple[0][0] + r'[\.]? '
            elif tuple[1] in ('AD', 'AG'):
                lista = tuple[0].split('[ \-]')
                for l in lista:
                    if l[0].istitle():
                        contraccion+=l[0] + r'[\.]? '
                    else:
                        contraccion+= l + ' '
            else:
                contraccion = tuple[0].strip()
                if contraccion.find('.')>=0:
                    contraccion = contraccion.replace('.','\.?') 
                else:
                    contraccion += '\.?'
            return contraccion.strip()

    def _contrae_1er_apellido(self, apellido):
        if apellido.find('-'):
            apellidos = apellido.split('-')
            name_buffer = apellidos[0]
            for a in apellidos:
                if apellidos[0]!=a:
                    if a[0].istitle():
                        name_buffer += ' ' + a[0] + '[\.]?'
            return name_buffer
        else:
            return apellido
        return apellido

    
     # Some of the functions in this module takes flags as optional parameters:
     #        I  IGNORECASE  Perform case-insensitive matching.
        # lista = tree.flatten()
        # resultado = ''
        # print tree
        # for l in lista:
        #     resultado += l + ' ' 
        # return resultado.strip()
    def _literal(self, tree):
        #logging.debug('literal.tree= '+str(tree))
        if len(tree.pos()) > 1:
            name_buffer = ''
            for rama in tree:
                name_buffer += self._literal(rama)                 
            return name_buffer
        else:
            tuple = tree.pos()[0]
            #logging.debug('literal.tuple= ' +str(tuple))
            if tree.node == 'AAA':
                return tuple[0] + '[ \-]+'
            if tuple[1] == 'I':
                #logging.debug ('entrando en if tuple[1]==I')
                ret_str = tuple[0].strip()
                if ret_str.find('.')>=0:
                    ret_str = ret_str.replace('.','\.?')
                    #logging.debug('after replace initial with \., ret_str=' +ret_str)
                else:
                    ret_str += '\.?'
                    #logging.debug('after replace initial without \., ret_str=' +ret_str)
                return ret_str + ' '
            else:
                return tuple[0] + ' '
             
        

    def _sin_inicial(self, tree):
        if len(tree.pos()) > 1:
            name_buffer = ''
            for rama in tree:
                name_buffer += self._sin_inicial(rama) + ' '
            return name_buffer.strip()
        else:
            tuple = tree.pos()[0]
            if tuple[1]!='I' and tuple[0]:
                return tuple[0]
            else:
                return ''


    def _corta_nombres(self, tree):
        pass



    def filtra(self, snippet_str):
        for regex in self._regex_list:
            snippet_limpio = self._limpieza.limpia_reservados_xml(snippet_str)
            snippet_str_sin_acentos = self._limpieza.limpia_acentos(snippet_limpio)
            #error bug correction JGF: 23/01/12::
            regex = '[^A-Za-z]'+regex+'[^A-Za-z]'
            logging.debug('Tree len(leaves)=' +str(len(self._trees[0].leaves()))+ ' list::'+str(self._trees[0].leaves()))
            logging.debug('FiltroNominal::processing name_variation: ' +regex+ ' on snippet ' +snippet_str_sin_acentos)
            leaves_list = self._trees[0].leaves()
            if len(leaves_list)==2:
            #special case for names with initial + lastname only (A Amaya)    
                if len(leaves_list[0])<=2:
                    if re.search(regex, snippet_str_sin_acentos):
                        logging.debug('\t--->nominal correference found::' + regex)
                        return True
                elif re.search(regex, snippet_str_sin_acentos, flags=re.IGNORECASE):
                    logging.debug('\t--->nominal correference found::' + regex)
                    return True
            elif re.search(regex, snippet_str_sin_acentos, flags=re.IGNORECASE):
                logging.debug('\t--->nominal correference found::' + regex)
                return True

    def _separa_iniciales(self, nombre):
        exit_nombre = nombre
        if not exit_nombre.isupper():
            logging.debug('exit_nombre.isupper():')
            secuencia_inicial_r = re.match(u'^[A-Z]{2,}',exit_nombre)
            if secuencia_inicial_r:
                logging.debug('if secuencia_inicial_r:')
                secuencia_inicial = secuencia_inicial_r.group(0)
                exit_nombre = ''
                for c in secuencia_inicial:
                    exit_nombre = exit_nombre + ' ' + c 
                exit_nombre += nombre.replace(secuencia_inicial,'')
        return exit_nombre
        


class Limpieza:
    def __init__(self):
        #TODO: support propper UTF-8 with NLTK!!!

        self._re_a=re.compile(u'[áâàä]')
        self._re_e=re.compile(u'[éèêëě]')
        self._re_i=re.compile(u'[íïîì]')
        self._re_o=re.compile(u'[óòôöø]')
        self._re_u=re.compile(u'[úùüû]')
        self._re_n=re.compile(u'[ñ]')
        self._re_c=re.compile(u'[ç]')
        self._re_y=re.compile(u'[ỳýÿŷÿ]')
        self._re_beta=re.compile(u'[ß]')
        self._re_A=re.compile(u'[ÁÀÄÂÅ]')
        self._re_E=re.compile(u'[ÉÈÊË]')
        self._re_I=re.compile(u'[ÍÌÏÎ]')
        self._re_O=re.compile(u'[ÓÒÔÖØ]')
        self._re_U=re.compile(u'[ÚÙÛÜ]')
        self._re_N=re.compile(u'[Ñ]')
        self._re_C=re.compile(u'[Ç]')
        self._re_S=re.compile(u'[Š]')


        
    def limpia_acentos(self, linea):
        linea_u = unicode(linea, 'utf-8')

        linea_u = self._re_a.subn('a',linea_u)[0]
        linea_u = self._re_e.subn('e',linea_u)[0]
        linea_u = self._re_i.subn('i',linea_u)[0]
        linea_u = self._re_o.subn('o',linea_u)[0]
        linea_u = self._re_u.subn('u',linea_u)[0]
        linea_u = self._re_n.subn('n',linea_u)[0]
        linea_u = self._re_c.subn('c',linea_u)[0]
        linea_u = self._re_y.subn('y',linea_u)[0]
        linea_u = self._re_beta.subn('ss',linea_u)[0]
        linea_u = self._re_A.subn('A',linea_u)[0]
        linea_u = self._re_E.subn('E',linea_u)[0]
        linea_u = self._re_I.subn('I',linea_u)[0]
        linea_u = self._re_O.subn('O',linea_u)[0]
        linea_u = self._re_U.subn('U',linea_u)[0]
        linea_u = self._re_N.subn('N',linea_u)[0]
        linea_u = self._re_C.subn('C',linea_u)[0]
        linea_u = self._re_S.subn('S',linea_u)[0]
        
        linea_a = linea_u.encode('ascii', 'ignore')
        return linea_a

    def limpia_reservados_xml(self, linea):
        r = linea.replace('&apos;',"'")
        r = r.replace('&lt;',"<")
        r = r.replace('&gt;',">")
        r = r.replace('&quot;','"')
        r = r.replace('&amp;',"&")
        return r
        
        
    


        
class NameParser:
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


class World:

## boolean: world.is_country()
## booulean: world.is_city()
    def __init__(self, countries=UNO_ROOT+'/resources/country_names.en.es.local.txt', cities=''):        
        self.countries_es = []
        self.countries_en = []
        countries = open(countries)
        for country in countries:
            triplet=country.split(',')
            if len(triplet)>=2:
                self.countries_en.append(triplet[0].strip().lower())
                self.countries_es.append(triplet[1].strip().lower())

    def is_country(self, country, lang='both'):
        if lang=='es':
            if country.strip().lower() in self.countries_es:
                return True
            else:
                return False
        elif lang=='en':
            if country.strip().lower() in self.countries_en:
                return True
            else:
                return False
        else:
            c = country.strip().lower()
            if (c in self.countries_es) or (c in self.countries_en):
                return True
            else:
                return False
## ************************************
## ******** ORGANIZACIONES ************
## ************************************

class Organizaciones:
    # Detecta y expandir acrónimos
    #el nombre de la organización viene separado por comas
    def __init__(self, organization_str = ''):
        global TOPIC_SEPARATOR
        #TODO self.abreviacion = Abreviaciones()
        self.detecta_lengua = DetectorLengua().detecta_lengua
        
    def consulta_organizaciones(self, query):
        lista_queries = []
        lista_orgs = query.split(TOPIC_SEPARATOR)
        for org in lista_orgs:
            lengua = self.detecta_lengua(org)
            query = Query(org.strip(), 'es')
            lista_queries.append(query)
            query = Query(org.strip(), 'en')
            lista_queries.append(query)
            if lengua not in ['en','es']:
                query = Query(org.strip(), lengua)
                lista_queries.append(query)
        return lista_queries
        # Detecta la lengua de la organización
        

class Temas:
    #separar también los temas con ;
    def __init__(self, topicos = ''):
        global TOPIC_SEPARATOR
        self.detecta_lengua = DetectorLengua().detecta_lengua
        self._freeling_es = Freeling('es', False, False)
        self._freeling_en = Freeling('en', False, False)
        self._freeling = None
        self._ren_en=re.compile('NN') 
        self._rej_en=re.compile('JJ')
        self._rer_en=re.compile('RB')
        self._ren_es=re.compile('N')
        self._rej_es=re.compile('V')
        self._rer_es=re.compile('A')
        
        self._res=re.compile('_') 

        #TODO: usar NLTK para el inglés

    def consulta_temas(self, topicos):
        lista_queries = []
        lista_temas = topicos.split(TOPIC_SEPARATOR)
        for t in lista_temas:
            logging.debug('Temas::consulta_temas processing ' +t)
            tema = t.strip()
            lengua = self.detecta_lengua(tema)
            if lengua == 'en':
                self._freeling = self._freeling_en
                self._ren = self._ren_en
                self._rej = self._rej_en
                self._rer = self._rer_en
            else:
                self._freeling = self._freeling_es
                lengua = 'es'
                self._ren = self._ren_es
                self._rej = self._rej_es
                self._rer = self._rer_es
            logging.debug('Temas::consulta_temas llamando a Freeling para ' +tema)
            l = self._freeling.tokenize(tema)
            ls = self._freeling.split(l,1)   
            ls = self._freeling.morfo(ls)  
            ls = self._freeling.postag(ls)  
            ls = self._freeling.sense(ls)  
            for s in ls:
                ws = s.get_words()
                buffer = ''
                for w in ws :
                    logging.debug("Temas::consulta_temas::" +w.get_form()+" "+w.get_lemma()+" "+w.get_parole())
                    if self._ren.match(w.get_parole()) or self._rej.match(w.get_parole()) or self._rer.match(w.get_parole()):
                        buffer = buffer + ' ' + self._res.sub(' ',w.get_form())
                        logging.debug('Temas::consulta_temas: appending to buffer:' +buffer)
                    elif len(buffer)>0:
                        query = Query(buffer.strip(), lengua)
                        lista_queries.append(query)
                        logging.debug('Temas::consulta_temas: appending to result::' +buffer)
                        buffer = ''
                if len(buffer)>0:
                    query = Query(buffer.strip(), lengua)
                    lista_queries.append(query)
                    logging.debug('Temas::consulta_temas: appending to result::' +buffer)
                       
        return lista_queries



## ************************************
## ******* CLASS FREELING *************
## ************************************
## usage:

    ## freeling = Freeling('en', False, False)
    ## lin="The dog is bad"

    ## l = freeling.tokenize(lin)
    ## ls = freeling.split(l,1)
    ## ls = freeling.morfo(ls)
    ## ls = freeling.postag(ls)
    ## ls = freeling.sense(ls)
    ## for s in ls:
    ##             ws = s.get_words()
    ##             for w in ws :
    ##                 #print w.get_form()+" "+w.get_lemma()+" "+w.get_parole()

class Freeling:    
    def __init__(self, language='en', named_entities=False, multi_word=False):

        global FREELING_LIB, FREELING_DATA
        self.lang = language
        self.ne = named_entities
        self.mw = multi_word
        
        logging.debug('Starting Freeling with LIB='+FREELING_LIB+' and DATA='+FREELING_DATA)
        op=libmorfo_python.maco_options(self.lang)
        if self.ne: i_ne = 0
        else: i_ne = 2
        if self.mw: i_mw = 1
        else: i_mw = 0
        op.set_active_modules(1,i_mw,1,1,1,1,1,1,i_ne,0)
        datalang_dir = FREELING_DATA + '/' + self.lang + '/'
        logging.debug ('Freeling::data_lang='+datalang_dir)
        op.set_data_files(datalang_dir+'locucions.dat', datalang_dir+'quantities.dat', datalang_dir+'afixos.dat', \
                          datalang_dir+'probabilitats.dat', datalang_dir+'maco.db', datalang_dir+'np.dat', \
                          FREELING_DATA+'/common/punct.dat', datalang_dir+'corrector/corrector.dat')
        
        self._tk=libmorfo_python.tokenizer(datalang_dir+"/tokenizer.dat")
        self._sp=libmorfo_python.splitter(datalang_dir+"/splitter.dat")
        self._mf=libmorfo_python.maco(op)

        self._tg=libmorfo_python.hmm_tagger(self.lang,datalang_dir+"/tagger.dat",1,2)
        self._sen=libmorfo_python.senses(datalang_dir+"/senses30.db",0)

    def tokenize(self,line):
        return self._tk.tokenize(line)

    def split(self,l,i):
        return self._sp.split(l,i)

    def morfo(self,ls):
        return self._mf.analyze(ls)

    def postag(self,ls):
        return self._tg.analyze(ls)

    def sense(self,ls):
        return self._sen.analyze(ls)

## ************************************
## **** LANGUAGE DETECTOR *************
## ************************************
class DetectorLengua:
    #TODO: don't go to google to do this
    #NLTK might have a language detection module
    def __init__(self):
        global GOOGLE_WAIT
        self.last_query_time = time.mktime( (1972,1,4,0,0,0,0,0,0) )
        self._espera = GOOGLE_WAIT
        self._detect = LanguageDetector().detect

    def detecta_lengua(self, texto):
        global OFFLINE
        if OFFLINE:
            return 'en'
        wait = time.time() - self.last_query_time
        logging.info('DetectorLengua::start waiting google at ' + time.ctime(time.time()))
        while wait < self._espera:
            wait = time.time() - self.last_query_time
            if wait < 0:
                logging.error('Time error waiting for google')
                break
        logging.info('DetectorLengua::end waiting google at ' + time.ctime(time.time()))
        try:
            lengua = self._detect(texto)
            logging.debug ('DetectaLengua::Language of '+texto+ ' = '+lengua.lang_code)
            return lengua.lang_code
        except DetectionError:
            logging.error ('Organizaciones::Language detection error on accronym' +texto)
            return ''


## ************************************
## **** FILTER TESING CLASSES ********
## ************************************

class TestFiltroNominal(object):
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        pass

    def variaciones(self, nombre):
        filtro_nominal = FiltroNominal(nombre)
        return filtro_nominal._regex_list
        
