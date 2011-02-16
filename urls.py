from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('yata.views',
    # Example:
    (r'^yata/$', 'index'),
    (r'^yata/add_task/$',              'edit'),
    (r'^yata/(?P<task_id>\d+)/edit/$', 'edit'),
    url(r'^yata/(?P<task_id>\d+)/mark_done/$', 'mark_done', name='mark-task-done'),
    url(r'^yata/(?P<task_id>\d+)/mark_not_done/$', 'mark_done', {'b': False}, name='mark-task-not-done'),
    (r'^yata/context/show/(?P<context_id>\d+)/$', 'select_context'),
    (r'^yata/context/show/all/$', 'select_context_all'),
    (r'^yata/context/show/none/$', 'select_context_none'),
    (r'^yata/context/add/$', 'edit_context'),
    (r'^yata/context/(?P<id>\d+)/edit/$', 'edit_context'),
    (r'^yata/context/(?P<id>\d+)/delete/$', 'delete_context'),
    (r'^yata/task/(?P<id>\d+)/delete/$', 'delete_task'),
    (r'^yata/xml/import/$', 'xml_import'),
    (r'^yata/xml/export/$', 'xml_export'),
    (r'^yata/future/show/$', 'show_future_tasks', {'b': True}),
    (r'^yata/future/hide/$', 'show_future_tasks', {'b': False}),
    (r'^yata/done/yes/$', 'show_tasks_done', {'b': 'Done'}),
    (r'^yata/done/no/$', 'show_tasks_done', {'b': 'Active'}),
    (r'^yata/done/all/$', 'show_tasks_done', {'b': 'All'}),
)

urlpatterns += patterns('',    
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    (r'^static_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.XNO_LOCAL_PREFIX+'public/static_media/', 'show_indexes': True }),    
)
