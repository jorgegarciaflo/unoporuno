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
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from unoporuno.models import Busqueda, Persona

def index(request):
    return render_to_response('unoporuno/index.html', None, context_instance=RequestContext(request))

def registro(request):
    return render_to_response('unoporuno/registro.html', None, context_instance=RequestContext(request))

def registra_usuario(request):
    nombre = request.POST['nombre']
    apellido = request.POST['apellido']
    email = request.POST['email']
    usuario = request.POST['usuario']
    clave = request.POST['clave']
    return HttpResponse(nombre + apellido + email + usuario + clave)
    
def login_cidesal(request):
    usuario = request.POST['usuario']
    clave = request.POST['clave']
    user = authenticate(username=usuario, password=clave)
    if user is not None:
        if user.is_active:
            login(request,user)
            busqueda_list = Busqueda.objects.all().order_by('-fecha')
            return render_to_response('unoporuno/lista_busquedas.html', {'busqueda_list': busqueda_list},
                              context_instance=RequestContext(request))
        else:
            str_error = 'El usuario existe pero no está activo: contacte al administrador.'
            return render_to_response('unoporuno/error.html', {'error_msg':str_error}, context_instance=RequestContext(request))
    else:
        str_error = 'Usuario o clave inválidos.'
        return render_to_response('unoporuno/error.html',{'error_msg':str_error}, context_instance=RequestContext(request))
    #return HttpResponse("logging in user:" + usuario + " with password:" + clave + " and result=" + str(user))
    
    ##return HttpResponse("your user= %s" % username)

@login_required
def lista_busquedas(request):
    busqueda_list = Busqueda.objects.all().order_by('-fecha')
    return render_to_response('unoporuno/lista_busquedas.html', {'busqueda_list': busqueda_list},
                              context_instance=RequestContext(request))
@login_required    
def busqueda(request, busqueda_id):

    b = get_object_or_404(Busqueda, pk=busqueda_id)
    orden_alfabetico = b.persona_set.all().order_by('name')
    return render_to_response('unoporuno/busqueda.html', {'busqueda': b, 'orden_alfabetico': orden_alfabetico},
                              context_instance=RequestContext(request))

#TODO
#def persona(request, persona_id):
#    return HttpResponse("You're looking at persona %s " % persona_id)
@login_required
def persona(request, busqueda_id, persona_id, pipeline_id, features):
    return render_to_response('unoporuno/persona.html', context_instance=RequestContext(request))

@login_required
def options (request, busqueda_id, persona_id, pipeline_id, features):
    return render_to_response('unoporuno/options.html', {'busqueda_id':busqueda_id,
                                                         'persona_id': persona_id,
                                                         'pipeline_id': pipeline_id,
                                                         'features': features},
                              context_instance=RequestContext(request))
@login_required    
def pipeline(request, busqueda_id, persona_id, pipeline_id, features):
    #return HttpResponse("features %s " % features)
    lista_snippet = []
    p = get_object_or_404(Persona, pk=persona_id)
    if features == '0' and pipeline_id=='top':
        lista_snippet = p.snippet_set.filter(FG=1).exclude(RE=1).filter(converging_pipelines=1)[:5]
    elif features == '0' and pipeline_id=='all': 
        lista_snippet = p.snippet_set.filter(FG=1).exclude(RE=1).order_by('-evidence_type')
    elif features != '0':
        if features.isdigit():
            lista_snippet = p.snippet_set.filter(FG=1).exclude(RE=1).extra(\
                where=['RE_Features & ' +features+ '>= ' +features]).order_by('-evidence_type')
        else:
            lista_snippet = p.snippet_set.filter(FG=1).exclude(RE=1).order_by('-converging_pipelines')[:5]
        
    # elif pipeline_id == 'top':
    #     lista_snippet = p.snippet_set.filter(converging)
    #     for snippet in p.snippet_set.filter(converging_pipelines='4').filter(FG=1):
    #         lista_snippet.append(snippet)
    #     if len(lista_snippet)<10:
    #         for snippet in p.snippet_set.filter(converging_pipelines='3').filter(FG=1):
    #             lista_snippet.append(snippet)
    #         if len(lista_snippet)<10: 
    #             for snippet in p.snippet_set.filter(converging_pipelines='2').filter(FG=1):
    #                 if len(lista_snippet)<10:
    #                     lista_snippet.append(snippet)
    #                 else:
    #                     break
    #             if len(lista_snippet)<10:
    #                 for snippet in p.snippet_set.filter(converging_pipelines='1').filter(FG=1):
    #                     if len(lista_snippet)<10:
    #                         lista_snippet.append(snippet)
    #                     else:
    #                         break
    return render_to_response('unoporuno/pipeline.html',\
                              {'persona': p, 'busqueda_id': busqueda_id,
                               'lista_snippet':lista_snippet}, \
                              context_instance=RequestContext(request))
@login_required
def evalua(request, busqueda_id, persona_id):
    #TODO: checar que el snippet pertenezca a la vista OJO TOP10
    p = get_object_or_404(Persona, pk=persona_id)        
    org_feature = ''
    combo_value = ''
    for snippet in p.snippet_set.all():
        u_snippet_id = unicode(snippet.id)
        u_combo_id = unicode('combo') + unicode(snippet.id)
        try:
            checked = request.POST[u_snippet_id]
            combo_value = request.POST[u_combo_id]
        except KeyError:
            snippet.pertinente = False
            snippet.save()
            continue
        else:
            snippet.pertinente = True
            i_combo_value = int(combo_value)
            snippet.evidence_type = i_combo_value
            snippet.save()
    
    mobility_value = request.POST[u'mobility_status']
    i_mobility = int(mobility_value) if mobility_value else 0
    if i_mobility>0:
        p.mobility_status = i_mobility
        p.save()
    return HttpResponseRedirect(reverse('unoporuno.views.busqueda', args=(busqueda_id,)))
    #return HttpResponse("combo_value %s " % combo_value)

@login_required
def busca(request, busqueda_id, persona_id, pipeline_id, features):
    
    new_pipeline = request.POST['pipeline']
    #quince como el número de features que estamos trabajando
    #cada features está representada en un bit 
    features_value = 0
    features_vector = range(15)
    for f in features_vector:
        try:
            checked = request.POST[str(f)]
        except KeyError:
            continue
        else:
            features_value += 2**f

    return HttpResponseRedirect(reverse('unoporuno.views.pipeline', args=(busqueda_id, persona_id, new_pipeline, features_value)))

@login_required
def vincula(request, busqueda_id, persona_id):
    b = get_object_or_404(Busqueda, pk=busqueda_id)
    p = get_object_or_404(Persona, pk=persona_id)
    lista_vinculos = []
    lista_vinculos = p.vinculo_set.all().order_by('tipo')
    return render_to_response('unoporuno/vinculos.html', {'busqueda':b, 'persona':p, 'lista_vinculos':lista_vinculos},
                              context_instance=RequestContext(request))
