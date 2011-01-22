from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^xno/', include('xno.foo.urls')),
    (r'^yata/$', 'yata.views.index'),
    (r'^yata/(?P<task_id>\d+)/mark_done/$', 'yata.views.mark_done'),
    (r'^yata/(?P<task_id>\d+)/mark_not_done/$', 'yata.views.mark_not_done'),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
