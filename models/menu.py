# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

response.menu = [
    (T('Home'), False, URL('default', 'index'), []), 
    
]


def append_admin_menu():
    admin_menu = [
            ('Admin', False, '#', [
                ('Books', False, URL('admin', 'manage_book'), []),
                ('Authors', False, URL('admin', 'manage_author'), []),
                ('Authors & Books', False, URL('admin', 'authors_and_books'), []),
                ('Submit Copies', False, URL('admin', 'new_hofb'), []),
                ('Handled Books', False, URL('admin', 'handling_of_the_book'), []),
                ('Requested Books', False, URL('admin', 'requested_books'), []),
                ('Past Book Orders', False, URL('admin', 'past_book_orders'), []),
                ('Users overview', False, URL('admin', 'user_overview'), []),
                ]
            )
    ]
    if auth.user != None:
        for groupname in auth.user_groups.values():
            if groupname  == 'admins':
                response.menu += admin_menu

def append_user_menu():
    user_menu = [
            #('All Books', False, URL('default', 'book_overview'), []),
            ('Order Books', False, URL('user', 'book_overview'), []),
            ('My Books', False, '#',[
                ('Active orders', False, URL('user', 'active_orders'), []),
                ('Past orders', False, URL('user', 'past_orders'), []),
            ])
    ]


    

    #auth.user is a variable that contains the currently logged in user details
    #auth.user_group is a dictionary that lists all groups the currently logged in user is member of
    if auth.user != None:
        for groupname in auth.user_groups.values():
            if groupname == 'approved_user':
                response.menu +=user_menu
        

append_admin_menu()
append_user_menu()
# ----------------------------------------------------------------------------------------------------------------------
# provide shortcuts for development. you can remove everything below in production
# ----------------------------------------------------------------------------------------------------------------------

if not configuration.get('app.production') and 1==9:
    _app = request.application
    response.menu += [
        (T('My Sites'), False, URL('admin', 'default', 'site')),
        (T('This App'), False, '#', [
            (T('Design'), False, URL('admin', 'default', 'design/%s' % _app)),
            (T('Controller'), False,
             URL(
                 'admin', 'default', 'edit/%s/controllers/%s.py' % (_app, request.controller))),
            (T('View'), False,
             URL(
                 'admin', 'default', 'edit/%s/views/%s' % (_app, response.view))),
            (T('DB Model'), False,
             URL(
                 'admin', 'default', 'edit/%s/models/db.py' % _app)),
            (T('Menu Model'), False,
             URL(
                 'admin', 'default', 'edit/%s/models/menu.py' % _app)),
            (T('Config.ini'), False,
             URL(
                 'admin', 'default', 'edit/%s/private/appconfig.ini' % _app)),
            (T('Layout'), False,
             URL(
                 'admin', 'default', 'edit/%s/views/layout.html' % _app)),
            (T('Stylesheet'), False,
             URL(
                 'admin', 'default', 'edit/%s/static/css/web2py-bootstrap3.css' % _app)),
            (T('Database'), False, URL(_app, 'appadmin', 'index')),
            (T('Errors'), False, URL(
                'admin', 'default', 'errors/' + _app)),
            (T('About'), False, URL(
                'admin', 'default', 'about/' + _app)),
        ]),

    ]
