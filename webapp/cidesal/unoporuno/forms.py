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
from tempfile import NamedTemporaryFile
from django import forms
import magic

class LanzaBusqueda(forms.Form):
    nombre = forms.CharField(max_length=100, required=True)
    descripcion = forms.CharField(max_length=200, required=False)
    file = forms.FileField(required=True)


class InputFile(object):
    def __init__(self,archivo):
        __mime = magic.open(magic.MAGIC_MIME)
        __mime.load()
        f = NamedTemporaryFile(delete=False)
        self.name = f.name
        with f.file as destination:
            for chunk in archivo.chunks():
                destination.write(chunk)
        self.mime_type = __mime.file(self.name)
        self.file = f.file
        
      
        

