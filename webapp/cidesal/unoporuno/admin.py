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
from unoporuno.models import Busqueda, Persona, Snippet
from django.contrib import admin


class PersonasInline(admin.TabularInline):
    model = Persona
    extra = 1
    fieldsets = [
        (None, {'fields':['name']}),
        (None, {'fields':['geo']}),
        (None, {'fields':['orgs']}),
        (None, {'fields':['topics']}),
        ]
    list_display = ('name','geo','orgs','topics')

class BusquedaAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Nombre', {'fields':['nombre']}),
        ('Fecha', {'fields':['fecha']}),
        ('Usuario', {'fields':['usuario']}),
        ('Descripción', {'fields':['descripcion']}),
        ]
    inlines = [PersonasInline]
    list_display = ('nombre', 'fecha', 'descripcion')

class SnippetsInline(admin.TabularInline):
    model = Snippet
    extra = 3
    fieldsets = [
        ('Consulta', {'fields':['query']}),
        ('Titulo', {'fields':['title']}),
        ('Descripcion', {'fields':['description']}),
        ('Vínculo', {'fields':['link']}),
        ('F.nominal', {'fields':['FG']}),
        ]
    list_display = ('query','title','description','link','FG')

class PersonaAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Nombre', {'fields':['name']}),
        ('Lugares', {'fields':['geo']}),
        ('Organizaciones', {'fields':['orgs']}),
        ('Temas', {'fields':['topics']}),
        ('Vínculo buscado', {'fields':['link']}),
        ]
    inlines = [SnippetsInline]
    list_display = ('name','geo')

admin.site.register(Busqueda, BusquedaAdmin)
admin.site.register(Persona, PersonaAdmin)
