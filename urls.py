from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',    
    (r'^yata/', include('yata.urls')),
    (r'^yata/accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^yata/accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'registration/logout.html'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    (r'^static_media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.XNO_LOCAL_PREFIX+'public/static_media/', 
        'show_indexes': True 
    }),    
)
