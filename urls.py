from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^yata/$', 'yata.views.index'),
    (r'^yata/add_task/$', 'yata.views.add_task'),
    (r'^yata/(?P<task_id>\d+)/mark_done/$', 'yata.views.mark_done'),
    (r'^yata/(?P<task_id>\d+)/mark_not_done/$', 'yata.views.mark_done', {'b': False}),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    
    (r'^static_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.XNO_LOCAL_PREFIX+'public/static_media/', 'show_indexes': True }),    
)
