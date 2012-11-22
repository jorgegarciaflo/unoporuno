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
from django.db import models

class Busqueda(models.Model):
    nombre = models.CharField(max_length=200)
    fecha = models.DateTimeField('fecha de búsqueda')
    usuario = models.CharField(max_length=200, blank=True)
    descripcion = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=2, blank=True)
    # OK = búsqueda terminada
    # @ = buscando
    # x = error7
    def __unicode__(self):
        return self.nombre
    
class Persona(models.Model): 
    busqueda = models.ForeignKey(Busqueda)
    name = models.CharField(max_length=250)
    geo = models.CharField(max_length=300, blank=True)
    orgs = models.CharField(max_length=400, blank=True)
    topics = models.CharField(max_length=400, blank=True)
    link = models.CharField(max_length=400, blank=True)
    prediction = models.IntegerField(null=True)
    mobility_status = models.IntegerField(null=True)
    #linked_persons = models.TextField(null=True)
    #linked_locations = models.TextField(null=True)
    #linked_organizations = models.TextField(null=True)
    # mobility_status/prediction code:
    #      3 : N/A
    #      2 : local
    #      1 : mobile
    #      None: ?

    # sólo para mobility_status:
    # 11 = mobile.lineal
    # 12 = mobile.circular
    # 31 = extranjero
    
    def __unicode__(self):
        return self.name

class Snippet(models.Model):
    persona = models.ForeignKey(Persona)
    query = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    description = models.CharField(max_length=400)
    link = models.CharField(max_length=400)
    FG = models.NullBooleanField('nominal filter')
    #RE is being used for blacklisted http addresses
    #RE=1 , blacklisted website
    #blacklist at $UNOPORUNO_ROOT/resources/regex/blacklist.regex
    RE = models.NullBooleanField('biogeographic filter')
    RE_score = models.DecimalField('biogeographic filter score', max_digits=10, decimal_places=9, null=True)
    #El campo R_score es un vector binario de features
    # see: UNOPORUNO_ROOT/scripts/unoporuno_feature_annotation.py
    #      UNOPORUNO_ROOT/resources/regex/*.regex
    #      UNOPORUNO_ROOT/resources/gazetteer/*.gazt
    #bit 2*0 = 1  organization feature 
    #bit 2*1 = 2  country 
    #bit 2*2 = 4 city
    #bit 2*3 = 8 accronym
    #bit 2*4 = 16 biographical phrases
    #bit 2*5 = 32 profession
    #bit 2*6 = 64 degree
    #bit 2*7 = 128 CV
    #bit 2*8 = 256 name_in_http
    #bit 2*9 = 512 latinamerican nationality
    #bit 2*10 = 1024 world nationality
    #bit 2*11 = 2048 email
    #bit 2*12 = 4096 scientifc publication
    #bit 2*13 = 8192 Linked in
    #bit 2*14 = 16384 PhD thesis
    ESA_score = models.DecimalField('semantic filter score', max_digits=10, decimal_places=9, null=True)
    RE_features =  models.IntegerField('binary features', null=True)
    converging_pipelines = models.IntegerField(null=True)
    name_pipeline = models.NullBooleanField()
    geo_pipeline = models.NullBooleanField()
    orgs_pipeline = models.NullBooleanField()
    topics_pipeline = models.NullBooleanField()
    pertinente = models.NullBooleanField('¿vínculo útil?')
    evidence_type = models.IntegerField(null=True)
    featured_countries = models.CharField(max_length=100)

class Vinculo(models.Model):
    persona = models.ForeignKey(Persona)
    nombres = models.TextField(null=True)
    lugares = models.TextField(null=True)
    organizaciones = models.TextField(null=True)
    descripcion = models.CharField(max_length=50,null=True)
    tipo = models.IntegerField(null=True)


    def __unicode__(self):
        return self.query +' :: '+ self.title

