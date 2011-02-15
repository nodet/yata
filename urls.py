from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^yata/$', 'yata.views.index'),
    (r'^yata/add_task/$',              'yata.views.edit'),
    (r'^yata/(?P<task_id>\d+)/edit/$', 'yata.views.edit'),
    url(r'^yata/(?P<task_id>\d+)/mark_done/$', 'yata.views.mark_done', name='mark-task-done'),
    url(r'^yata/(?P<task_id>\d+)/mark_not_done/$', 'yata.views.mark_done', {'b': False}, name='mark-task-not-done'),
    (r'^yata/context/show/(?P<context_id>\d+)/$', 'yata.views.select_context'),
    (r'^yata/context/show/all/$', 'yata.views.select_context_all'),
    (r'^yata/context/show/none/$', 'yata.views.select_context_none'),
    (r'^yata/context/add/$', 'yata.views.edit_context'),
    (r'^yata/context/(?P<id>\d+)/edit/$', 'yata.views.edit_context'),
    (r'^yata/context/(?P<id>\d+)/delete/$', 'yata.views.delete_context'),
    (r'^yata/task/(?P<id>\d+)/delete/$', 'yata.views.delete_task'),
    (r'^yata/xml/import/$', 'yata.views.xml_import'),
    (r'^yata/xml/export/$', 'yata.views.xml_export'),
    (r'^yata/future/show/$', 'yata.views.show_future_tasks', {'b': True}),
    (r'^yata/future/hide/$', 'yata.views.show_future_tasks', {'b': False}),
    (r'^yata/done/yes/$', 'yata.views.show_tasks_done', {'b': 'Done'}),
    (r'^yata/done/no/$', 'yata.views.show_tasks_done', {'b': 'Active'}),
    (r'^yata/done/all/$', 'yata.views.show_tasks_done', {'b': 'All'}),
    
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    
    (r'^static_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.XNO_LOCAL_PREFIX+'public/static_media/', 'show_indexes': True }),    
)
