#-*-coding:utf-8 -*-

from celery import task
from search_task import UnoporunoSearch


@task()
def add(x,y):
    return x+y

@task()
def task_lanza_busqueda(nombre, archivo, usuario, descripcion=''):
    #valida archivo, si no es válido escribe la búqueda en estatus x
    #cuenta el número de registros en el archivo
    #escribe la búsqueda en @ (TODO: cuando trabajemos persona a persona, pondremos @n/TOTAL)
    #dale import a unoporuno_search
    #lanza la búsqueda en unoporuno_search
    unoporuno_search = UnoporunoSearch(nombre,archivo,usuario,descripcion)
    unoporuno_search.busca()
    return usuario
     
