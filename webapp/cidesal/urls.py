from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('unoporuno.views',
                       url(r'^unoporuno/', include('unoporuno.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       ) 
    # Examples:
    # url(r'^$', 'cidesal.views.home', name='home'),
    # url(r'^cidesal/', include('cidesal.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

