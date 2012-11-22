#-*- coding:utf-8 -*-
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
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('unoporuno.views', 
                   url(r'^$','lista_busquedas'),
                   url(r'login/', 'show_login'),
                   url(r'login_cidesal/', 'login_cidesal'),
                   url(r'logout/', 'logout_cidesal'),
                   url(r'registro/', 'registro'),
                   url(r'registra_usuario/', 'registra_usuario'),
                   url(r'lanza_busqueda/', 'lanza_busqueda'),                           
                   url(r'busquedas/','lista_busquedas'),
                   url(r'busqueda/(?P<busqueda_id>\d+)/$', 'busqueda'),
                   url(r'busqueda/(?P<busqueda_id>\d+)/persona/(?P<persona_id>\d+)/(?P<pipeline_id>(top|all))/(?P<features>\d+)/$', 'persona'),
                   url(r'busqueda/(?P<busqueda_id>\d+)/persona/(?P<persona_id>\d+)/(?P<pipeline_id>(top|all))/(?P<features>\d+)/options.html$', 'options'),
                   url(r'busqueda/(?P<busqueda_id>\d+)/persona/(?P<persona_id>\d+)/(?P<pipeline_id>(top|all))/(?P<features>\d+)/pipeline.html$', 'pipeline'),
                   url(r'busqueda/(?P<busqueda_id>\d+)/persona/(?P<persona_id>\d+)/evalua/$', 'evalua'),
                   url(r'busqueda/(?P<busqueda_id>\d+)/persona/(?P<persona_id>\d+)/pipeline/(?P<pipeline_id>(top|all))/(?P<features>\d+)/busca/$', 'busca'),
                   url(r'busqueda/(?P<busqueda_id>\d+)/persona/(?P<persona_id>\d+)/vinculos/$', 'vincula'),
                    )
  

