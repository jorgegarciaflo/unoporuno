#-*-coding:utf-8 -*-
import sys
from celery import task
from search_task import UnoporunoSearch
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@task(time_limit=5184000, ignore_results=True)
def task_lanza_busqueda(nombre, archivo, usuario, descripcion=''):
    #valida archivo, si no es válido escribe la búqueda en estatus x
    #cuenta el número de registros en el archivo
    #escribe la búsqueda en @ (TODO: cuando trabajemos persona a persona, pondremos @n/TOTAL)
    #dale import a unoporuno_search
    #lanza la búsqueda en unoporuno_search
    try:
        UnoporunoSearch(nombre,archivo,usuario,descripcion)
    except:
        #TODO: escribir el error en la base de datos
        logger.info('Error en la ejecución de la tarea:' + str(sys.exc_info()))
        pass
     
 
