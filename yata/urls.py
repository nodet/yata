from django.conf.urls.defaults import *

urlpatterns = patterns('yata.views',
    # Example:
    (r'^$',                                  'index'),

 url(r'^task/new/$',                         'edit_task', name='add-task'),
    (r'^task/(?P<id>\d+)/edit/$',            'edit_task'),
    (r'^task/(?P<id>\d+)/delete/$',          'delete_task'),
 url(r'^task/(?P<id>\d+)/mark_done/$',       'mark_done',                name='mark-task-done'),
 url(r'^task/(?P<id>\d+)/mark_not_done/$',   'mark_done', {'b': False}, name='mark-task-not-done'),

    (r'^context/show/(?P<context_id>\d+)/$', 'select_context'),
    (r'^context/show/all/$',                 'select_context_all'),
    (r'^context/show/none/$',                'select_context_none'),
 url(r'^context/add/$',                      'edit_context', name='add-context'),
    (r'^context/(?P<id>\d+)/edit/$',         'edit_context'),
    (r'^context/(?P<id>\d+)/delete/$',       'delete_context'),
    
    (r'^xml/import/$',                       'xml_import'),
    (r'^xml/export/$',                       'xml_export'),
    
 url(r'^future/show/$',                      'show_future_tasks', {'b': True}, name='show-future-tasks'),
 url(r'^future/hide/$',                      'show_future_tasks', {'b': False}, name='hide-future-tasks'),
    
 url(r'^done/yes/$',                         'show_tasks_done', {'b': 'Done'}, name='show-done-tasks'),
 url(r'^done/no/$',                          'show_tasks_done', {'b': 'Active'}, name='show-active-tasks'),
 url(r'^done/all/$',                         'show_tasks_done', {'b': 'All'}, name='show-all-tasks'),
 
    (r'^accounts/new/$',                      'edit_user'),

)
