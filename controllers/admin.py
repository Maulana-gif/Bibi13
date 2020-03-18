# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################


@auth.requires_membership('admins')
def manage_author():
    mydb.author.image.represent = lambda image, row: IMG(_src=URL('admin', 'download', args=image), 
                                                    
                                                    _class='author_image',
                                                    _width='50px',
                                                    _onclick='$("#image_container").attr("src","'+URL("admin", "download", args=image)+'");document.getElementById("text_container").innerHTML = "'+str(row.name)+'"; $("#imageModal").modal("show");',
                                                    )    if image else ''
                                                      
    grid = SQLFORM.grid(mydb.author,
                        headers={'author.image':'Autor'},
                    #user_signature=False    #http://www.web2py.com/books/default/chapter/29/07/forms-and-validators#SQLFORM-grid, do not check login
                    showbuttontext = False
                    )
    #return locals()
        
    return {'author': grid}
    

@auth.requires_membership('admins')
def manage_book():
    mydb.book.image.represent = lambda image, row: IMG(_src=URL('admin', 'download', args=image), 
                                                _class='book_image',
                                                _width='50px',
                                                _onclick='$("#image_container").attr("src","'+URL("admin", "download", args=image)+'");document.getElementById("text_container").innerHTML = "'+str(row.book[row] if 'trailer' in row.book else '')+'"; $("#imageModal").modal("show");',
                                                ) if image else ''

    mydb.author.image.represent = lambda image, row: IMG(_src=URL('admin', 'download', args=image), 
                                                _class='author_image',
                                                _width='50px',
                                                _onclick='$("#image_container").attr("src","'+URL("admin", "download", args=image)+'");document.getElementById("text_container").innerHTML = "'+str(row.author['name'] if 'name' in row.author else row.as_dict())+'"; $("#imageModal").modal("show");',
                                                )    if image else ''  
    mydb.author.name.readable = False

    grid = SQLFORM.grid(mydb.book,
                     left = [ mydb.author.on( mydb.book.author == mydb.author.id )], 
                     fields = [ mydb.book.title, mydb.book.publish_date, mydb.book.isbn,mydb.book.trailer, mydb.book.image, mydb.author.image,  mydb.author.name], 
                    #user_signature=False,
                    maxtextlength=200,
                    showbuttontext = False,
                    headers={'book.image':'Buch','author.image':'Autor'}
                    
                    )
 
                                              

    return {'books':grid}

def download():
    return response.download(request, mydb)

#todo: receive variable quantities. x_number_of_quantities = book_copy.

'''
TOOD
- set the grid so that adding new entries is not allowed
- add a custom button in the corresponding view pointing to new_hofb()
'''

@auth.requires_membership('admins')
def handling_of_the_book():
    grid = SQLFORM.grid(mydb.handling_of_the_book,
                    #user_signature=True,
                    maxtextlength=200,
                    showbuttontext = False,
                    )
 
    return {'handling_of_the_book':grid}



def finish_book_order(i_status, i_status_2, i_check_in):
    logger.debug('finish_book_order with arguments {} {} {}'.format(i_status, i_status_2, i_check_in))
    hb_id = mydb( mydb.book_order_checkout.id == request.args(0) ).select( mydb.book_order_checkout.handling_of_the_book )[0]["handling_of_the_book"] #get id of handle table
    logger.debug('book id: {}'.format(hb_id))
    mydb(mydb.handling_of_the_book.id == hb_id).update(status=i_status)
    order_row = mydb( mydb.book_order_checkout.id == request.args(0) ).select()[0] #get row of table 'book_order_checkout'
    mydb(mydb.book_order_checkout.id == request.args(0)).delete() #delete row in table 'book_order_checkout'
    mydb.book_order_past.insert(check_out=order_row['check_out'],check_in=i_check_in,username=order_row['username'],user_id=order_row['user_id'],status=i_status_2,handling_of_the_book=hb_id) #backup oder in backup table
    redirect(URL('admin', 'requested_books')) #redirect back to checkin page

@auth.requires_membership('admins')
def lost_book():
    #TODO fix, read book id from argument and then update the record
    finish_book_order(19, 19, '')
    
@auth.requires_membership('admins')
def checkin_book():
    #TODO fix, read book id from argument and then update the record
    finish_book_order(17, 24, request.now)
    
@auth.requires_membership('admins')
def checkout():
    #TODO fix, read book id from argument and then update the record
    hb_id = mydb( mydb.book_order_checkout.id == request.args(0) ).select( mydb.book_order_checkout.handling_of_the_book )[0]["handling_of_the_book"] #get id of handle table
    mydb(mydb.handling_of_the_book.id == hb_id).update(status=22) #set status to 'checked out' 
    mydb(mydb.book_order_checkout.id == request.args(0)).update(status=22, check_out=request.now) #set status in table 'book_order_checkout' to 'checked out' and set check out date
    redirect(URL('admin', 'requested_books')) #redirect back to checkin page
    
@auth.requires_membership('admins')
def checkin():
    grid = SQLFORM.grid(mydb.book_order_checkout.status == 22, #get books with status 'checked out'
                     left = [ mydb.handling_of_the_book.on( mydb.handling_of_the_book.id == mydb.book_order_checkout.handling_of_the_book ), #left join handling table
                              mydb.book.on( mydb.handling_of_the_book.book == mydb.book.id )], #left join book tabke
                     fields = [ mydb.book_order_checkout.id, mydb.book.title,mydb.book_order_checkout.user_id, mydb.book_order_checkout.username, mydb.book_order_checkout.check_out ], #fields to display
                     deletable = True,
                     editable = True,
                     create = False,
                     maxtextlength=100,
                     details = False,
                     csv = False,
                     links=[lambda row: A(T('Check in'), #button for checking in a book
                     _href=URL('admin', 'checkin_book', args=row.book_order_checkout.id),
                     _class='button btn btn-default',
                     _name='btnUpdate'
                     ),
                     lambda row: A(T('Lost'), #button for marking a book as lost
                     _href=URL('admin', 'lost_book', args=row.book_order_checkout.id),
                     _class='button btn btn-default',
                     _name='btnUpdate',
                     showbuttontext = False,
                     )
                     ]
                       )
    return {'checkin':grid}



@auth.requires_membership('admins')
def requested_books():
    grid = SQLFORM.grid( mydb( (mydb.book_order_checkout.status == 21) | (mydb.book_order_checkout.status == 22) ),
                     left = [ mydb.handling_of_the_book.on( mydb.handling_of_the_book.id == mydb.book_order_checkout.handling_of_the_book ), #left join handling table
                              mydb.book.on( mydb.handling_of_the_book.book == mydb.book.id )], #left join book table
                     fields = [ mydb.book_order_checkout.status, mydb.book_order_checkout.id, mydb.book.title,mydb.book.image, mydb.book_order_checkout.user_id, mydb.book_order_checkout.username, mydb.book_order_checkout.check_out ], #fields to be displayed
                     deletable = False,
                     editable = False,
                     create = False,
                     maxtextlength=100,
                     details = False,
                     csv = False,
                     links=[ lambda row: create_buttons(row)],
                     showbuttontext = False
        )

    return dict(grid=grid)

def create_buttons(row):
    buttons = []
    if(row.book_order_checkout.status == 21):
        return A(T('Check out'), #button for checking in a book
                     _href=URL('admin', 'checkout', args=row.book_order_checkout.id),
                     _class='button btn btn-default',
                     _name='btnUpdate'
                     )
    elif(row.book_order_checkout.status == 22):
        return DIV(A(T('Check in'),
                      _href=URL('admin', 'checkin_book', args=row.book_order_checkout.id),
                     _class='button btn btn-default',
                     _name='btnUpdate'
                     ) +
                 A(T('Lost'), #button for checking in a book
                     _href=URL('admin', 'lost_book', args=row.book_order_checkout.id),
                     _class='button btn btn-default',
                     _name='btnUpdate'
                     ))
    return ''

@auth.requires_membership('admins')
def past_book_orders():
    grid = SQLFORM.grid(mydb( mydb.book_order_past ), #show past book orders for logged in user
                     left = [ mydb.handling_of_the_book.on( mydb.handling_of_the_book.id == mydb.book_order_past.handling_of_the_book ), #left join handling table
                              mydb.book.on( mydb.handling_of_the_book.book == mydb.book.id )], #left join book table
                     fields = [ mydb.book.title,mydb.book.image, mydb.book_order_past.check_out, mydb.book_order_past.username, mydb.book_order_past.check_in, mydb.book_order_past.status ],
                     editable = False,
                     maxtextlength=100,
                     details = False,
                     csv = False,
                     showbuttontext = False
                       ) 
    return dict(past_book_orders=grid)

#new_hofb() = new_handling_of_the_book():
def new_hofb():
    #creating a standard SQLFORM from the handling_of_the_book table
    form = SQLFORM(mydb.handling_of_the_book,
                    fields=['book', 'location'],
                    )
    #creating new quantity variables which are used to display an additional field to the form
    #as quantity is not part of the handling_of_the_book table
    quantity_label = LABEL('Quantity', _class='form-control-label col-sm-3', _for='handling_of_the_book_copy_quantity')
    quantity_input = DIV( 
                        INPUT(_name='quantity', _value=1, _type='number', _min="1", _id='handling_of_the_book_copy_quantity', _class='generic-widget form-control'),  
                        _class='col-sm-9' 
                        )
    quantity_element = DIV(  _class='form-group row', _id='handling_of_the_book_quantity__row')
    quantity_element.append(quantity_label)
    quantity_element.append(quantity_input)

    #adding quantity label and field, to the form, using the correct format (structure, classes, ids, ...)
    form[0].insert(-1, quantity_element)

    #TODO (1) handle the form input
    #TODO (2) create a new handling_of_the_book row "quantity" times, and insert them in the db
    #DONE (3) validate quantity (1 or more, error on 0 or negative)
    #DONE (4) tell the admin user the result of the action (ok, error)

    #attempting to get from variables and handle them (1 and 4, the rest if for later)
    #if form.accepts(request, session):
        #hell and damnation! the SQLFORM is inserting records automatically!!! I have to handle the additional values by hand... but how?
        #the work is done by the "accepts" method! nasty code!

    
    if form.process(onvalidation=new_hofb_validation, dbio=False).accepted:
        #we use the form vars, which are now validated
        book_id = int(form.vars.book)
        location_id = int(form.vars.location)
        quantity = int(form.vars.quantity)
        status = 17   #hard coding the status id, should be using a select but I do thid as placehodler, I'll do the select afterwards

        #TODO point (2)
        #create the records 
        #insert the records

        for n in range(quantity):
            mydb.handling_of_the_book.insert(book=book_id, status=17, location=location_id)

        request.vars.book = mydb( mydb.book.id == book_id ).select( mydb.book.title )[0]['title']
        request.vars.location = mydb( mydb.location.id == location_id ).select( mydb.location.location_name )[0]['location_name']
        response.flash = 'Books records created'
    elif form.errors:
        response.flash = 'Please check the form for errors'
    else:
        response.flash = 'Dear Librarian, here you can add new books to the library. Beware of rats'
        logger.warn('errors in the form {}'.format(request.vars))
    if request.vars.book is None:
        request.vars.book = ''
        request.vars.quantity = ''
        request.vars.location = ''
        
    return dict(form=form) 

'''
additional function to help validating the quantity in new_hofb form
'''
def new_hofb_validation(form):
    quantity = form.vars.quantity    #TODO check if quantity is in form.vars
    try:
        if quantity == None:                    #this should never happen as the html form should handle
            form.errors.quantity = "Quantity cannot be empty"
        elif int(quantity) < 1:                 #this should be handled by html5 number fields, but just in case...
            form.errors.quantity = "Quantity cannot be less than 1"
    except expression as identifier:
        form.errors.quantity = "Quantity must be a number"


def authors_and_books():
    #TODO reformat this as SQLFORM.grid
    
    '''
    t = TABLE()
    header = TR(TH('Author'), TH('Books count'), TH('Books'))
    authors_rows = mydb(mydb.author.id > 0).select()
    for author_row in authors_rows:
        r = TR()
        print '-----'
        print author_row.id, author_row.name
        r.append( TD(author_row.name) )
        books_rows = mydb(mydb.book.author == author_row.id).select()
        #print ('%s' % books_rows)
        count = 0
        for book in books_rows:
            count = count + 1
            print book.id, book.title
        
        #count = len(books_rows)
        r.append( TD(count) )

        link = A('books', _href=URL(works_of_the_author, args=[author_row.id])) 
        r.append( TD(link) )
        t.append(r)
    '''
    #TODO add counts column dict(header='name',body=lambda row: A(...))
    #TODO add link column (use the link attribute as by SQLFORM.grid in chapter 7)
    t = SQLFORM.grid( mydb.author,
                    #user_signature=False,
                     deletable = False,
                     editable = False,
                     create = False,
                     details = False,
                     csv = False,
                     links = [
                         {'header':'book_count','body':lambda row: _generate_author_books_count(row)},
                         {'header':'link_to_books', 'body':lambda row: A('link', _href=URL(works_of_the_author, args=[row.id]))}
                     ]
                    )
    return {'out':t}

@auth.requires_membership('admins')
def works_of_the_author():
    grid = SQLFORM.grid(mydb(mydb.book.author == request.args[0]),
                     fields = [mydb.book.title, mydb.book.publish_date, mydb.book.isbn],
                     user_signature=False,
                     maxtextlength=200,
                     showbuttontext = False
                     )
    return {'out':grid}

@auth.requires_membership('admins')
def user_overview():
    grid = SQLFORM.grid(db(db.auth_user),
                     left = [ db.auth_membership.on( db.auth_user.id == db.auth_membership.user_id ),
                              db.auth_group.on( db.auth_membership.group_id == db.auth_group.id  )],
                     fields = [db.auth_user.username, db.auth_user.first_name, db.auth_user.last_name, db.auth_group.role, db.auth_user.registration_key],
                     #user_signature=False,
                     maxtextlength=200,
                     links = [{'header':'', 'body':lambda row: _registration_button(row)}],
                     showbuttontext = False,
                     )
    return {'users':grid}

def _registration_button(row):
    
    try:
        btn = A('Status')
        registration_status = row.auth_user.registration_key
        '''
        using URL with vars, so each value will have it's corresponding key
        if I had used args, then they would be sent in order but without key
        vars:
         code: vars={'username':row.auth_user.username,'value':'active'}
         output: http://127.0.0.1:8000/Bibi2/admin/update_registration_status?username=andrea&value=active

        args: 
         code: args=[row.auth_user.username, 'active']
         output: http://127.0.0.1:8000/Bibi2/admin/update_registration_status?andrea&active
        '''
        if registration_status in ['pending', 'disabled', 'blocked']:  #TODO check the various user registration possible states in the documentation
            btn = A('Activate', _class = 'btn btn-success', _href= URL('update_registration_status', vars={'username':row.auth_user.username,'value':'activate'}))
        else:
            btn = A('Disable', _class = 'btn btn-danger', _href= URL('update_registration_status', vars={'username':row.auth_user.username,'value':'disable'}))    
        return btn
    except:
        return ''

@auth.requires_membership('admins')
def update_registration_status():
    #read arguments from url
    #eg http://127.0.0.1:8000/Bibi2/admin/update_registration_status?username=testUser&value=active
    #how to read vars
    username = request.vars['username'] if 'username' in request.vars else None
    value = request.vars['value'] if 'value' in request.vars else None

    out = None
    '''
    #how to read args
    username = request.args[0] if len(request.args) >= 1 else None
    value    = request.args[1] if len(request.args) >= 2 else None
    '''

    if (username != None and value != None):
        if (value == 'activate'):
            out = db(db.auth_user.username == username).update(registration_key=None)

        if (value == 'disable'):
            out = db(db.auth_user.username == username).update(registration_key='blocked')

        pass
    else:
        #do nothing because stuff is missing, or find a way to display some kind of unobstrusive error
        out = 0
    redirect(URL('admin', 'user_overview'))
    return out
    



def _generate_author_books_count( row ):

    books_rows = mydb(mydb.book.author == row.id).select()
    books_count = 0
    for book in books_rows:
        books_count = books_count + 1
    
    return books_count  

    '''
    option: from lambda call a function

    'count': lambda row:
             generate_count_of_books(books_rows)
             count = 0
             for book in books_rows:
                count = count + 1
             return count


    'link': lambda row:
            generate_author_book_link(link)

    def generate_count_of_books():

    def generate_author_book_link():        

    

        
    return {'out':t}
    '''
    


def free_books():
    return 0
