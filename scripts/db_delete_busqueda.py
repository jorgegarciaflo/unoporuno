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
#usage: python db_delete_busqueda id

import os, sys, ConfigParser, logging

logging.basicConfig(level=logging.INFO)
config = ConfigParser.ConfigParser()
config.read("unoporuno.conf")
if len(config.sections())==0:
    config.read(os.environ['HOME']+"/.unoporuno/unoporuno.conf")
    if len(config.sections())==0:
               logging.error("No configuration file on unoporuno.conf")
               exit(-1)

UNOPORUNO_ROOT = config.get('unoporuno', 'root')
UNOPORUNO_MODULES = UNOPORUNO_ROOT + '/module/'
CIDESAL_WEBAPP_PATH= UNOPORUNO_ROOT + '/webapp/'

if not UNOPORUNO_MODULES in sys.path:
    sys.path.append(UNOPORUNO_MODULES)
from busqueda_db import busqueda_db

if not CIDESAL_WEBAPP_PATH in sys.path:
    sys.path.append(CIDESAL_WEBAPP_PATH)
    sys.path.append(CIDESAL_WEBAPP_PATH+'cidesal/')
from unoporuno.models import Busqueda, Persona, Snippet

def main():
    logging.info ("busqueda_db::deleting busqueda_id:" +str(id))
    db_busqueda = busqueda_db.Busqueda_DB(UNOPORUNO_ROOT)    
    db_busqueda.delete(int(sys.argv[1]))
    
    
#mañana: borrar registros de manera limpia
#subir registros a la BD
#ponerle password
#filtrar nominal y biográfico

if __name__ == "__main__":
    main()
