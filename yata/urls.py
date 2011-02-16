from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('yata.views',
    # Example:
    (r'^$',                                  'index'),

    (r'^task/new/$',                         'edit_task'),
    (r'^task/(?P<id>\d+)/edit/$',            'edit_task'),
    (r'^task/(?P<id>\d+)/delete/$',          'delete_task'),
 url(r'^task/(?P<id>\d+)/mark_done/$',       'mark_done',                name='mark-task-done'),
 url(r'^task/(?P<id>\d+)/mark_not_done/$',   'mark_done', {'b': False}, name='mark-task-not-done'),

    (r'^context/show/(?P<context_id>\d+)/$', 'select_context'),
    (r'^context/show/all/$',                 'select_context_all'),
    (r'^context/show/none/$',                'select_context_none'),
    (r'^context/add/$',                      'edit_context'),
    (r'^context/(?P<id>\d+)/edit/$',         'edit_context'),
    (r'^context/(?P<id>\d+)/delete/$',       'delete_context'),
    
    (r'^xml/import/$',                       'xml_import'),
    (r'^xml/export/$',                       'xml_export'),
    
    (r'^future/show/$',                      'show_future_tasks', {'b': True}),
    (r'^future/hide/$',                      'show_future_tasks', {'b': False}),
    
    (r'^done/yes/$',                         'show_tasks_done', {'b': 'Done'}),
    (r'^done/no/$',                          'show_tasks_done', {'b': 'Active'}),
    (r'^done/all/$',                         'show_tasks_done', {'b': 'All'}),
)
