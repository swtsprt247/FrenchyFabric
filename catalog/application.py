from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import MainPage, Base, Categories

# authorization imports
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

# Referencing Client Secret File
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Frenchy Fabric Application"

engine = create_engine('sqlite:///frenchy_fabric.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("Finished!")
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        # if login_session['provider'] == 'facebook':
        #     fbdisconnect()
        #     del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showMerchandise'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showMerchandise'))


# Show all merchandise
@app.route('/')
@app.route('/frenchyfabric/')
def showMerchandise():
    main_page = session.query(MainPage).order_by(asc(MainPage.name))
    if 'username' not in login_session:
        return render_template('publicMerchandise.html', main_page=main_page)
    else:
        return render_template('merchandise.html', main_page=main_page)


# Create a new merchandise
@app.route('/frenchyfabric/new/', methods=['GET', 'POST'])
def newMerchandise():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newMerchandise = MainPage(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newMerchandise)
        flash('New Merchandise %s Successfully Created' % newMerchandise.name)
        session.commit()
        return redirect(url_for('showMerchandise'))
    else:
        return render_template('newMerchandise.html')


@app.route('/frenchyfabric/<int:main_page_id>/edit/', methods=['GET', 'POST'])
def editMerchandise(main_page_id):
    editedMerchandise = session.query(
        MainPage).filter_by(id=main_page_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedMerchandise.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit the Merchandise. Please put in your merchandise in order to edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedMerchandise.name = request.form['name']
            flash('Merchandise Successfully Edited %s' %
                  editedMerchandise.name)
            return redirect(url_for('showMerchandise'))
    else:
        return render_template('editMerchandise.html', main_pate=editedMerchandise)


# Delete a Merchandise
@app.route('/frenchyfabric/<int:main_page_id>/delete/', methods=['GET', 'POST'])
def deleteMerchandise(main_page_id):
    merchandiseToDelete = session.query(
        MainPage).filter_by(id=main_page_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if merchandiseToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete the merchandise. Please put in your own merchandise in order to delete.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(merchandiseToDelete)
        flash('%s Successfully Deleted' % merchandiseToDelete.name)
        session.commit()
        return redirect(url_for('showMerchandise', main_page_id=main_page_id))
    else:
        return render_template('deleteMerchandise.html', main_page=merchandiseToDelete)


# Show a merchandise (MainPage) Category
@app.route('/frenchyfabric/<int:main_page_id>/')
@app.route('/frencyfabric/<int:main_page_id>/categories/')
def showCategories(main_page_id):
    category = session.query(MainPage).filter_by(id=main_page_id).one()
    creator = getUserInfo(main_page.user_id)
    items = session.query(Categories).filter_by(
        main_page_id=main_page_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicCategories.html', items=items, main_page=main_page, creator=creator)
    else:
        return render_template('categories.html', items=items, main_page=main_page, creator=creator)


# Route for new Merchandise (MainPage) categories
@app.route('/frenchyfabric/<int:main_page_id>/new', methods=['GET', 'POST'])
def newCategoryItem(main_page_id):
    if 'username' not in login_session:
        return redirect('/login')
    merchandise = session.query(MainPage).filter_by(id=main_page_id).one()
    if login_session['user_id'] != main_page.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add category items to this Merchandise.');}</script><body onload='myFunction()'>"
        if request.method == 'POST':
            newItem = Categories(
                name=request.form['name'], description=request.form['description'], main_page_id=main_page_id, user_id=main_page.user_id)
            session.add(newItem)
            session.commit()
            flash('New Category %s Item Successfully Created' % (newItem.name))
            return redirect(url_for('showCategories', main_page_id=main_page_id))
    else:
        return render_template('NewCategoryItem.html', main_page_id=main_page_id)


# Route to edit categories
@app.route('/frenchyfabric/<int:main_page_id>/<int:categories_id>/edit/', methods=['GET', 'POST'])
def editCategoryItem(main_page_id, categories_id):
        if 'username' not in login_session:
            return redirect('/login')
    editedItem = session.query(Categories).filter_by(id=categories_id).one()
    merchandise = session.query(MainPage).filter_by(id=main_page_id).one()
    if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {alert('You are not authorized to the categories for this merchandise item.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash("Category has been edited!")
        return redirect(url_for('showCategories', main_page_id=main_page_id))
    else:
        return render_template('EditCategoryItem.html', main_page_id=main_page_id, categories_id=categories_id, i=editedItem)



# Route to delete categories
@app.route('/frenchyfabric/<int:main_page_id>/<int:categories_id>/delete/', methods=['GET', 'POST'])
def deleteCategoryItem(main_page_id, categories_id):
    if 'username' not in login_session:
    return redirect('/login')
    itemToDelete = session.query(Categories).filter_by(id=categories_id).one()
    merchandise = session.query(MainPage).filter_by(id=main_page_id).one()
     if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete categories from merchandise.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Category has been deleted!")
        return redirect(url_for('showCategories', main_page_id=main_page_id))
    else:
        return render_template('DeleteCategoryItem.html', i=deleteItem)



# Making an API Endpoint (GET Request)
@app.route('/frenchyfabric/<int:main_page_id>/category/JSON')
def MainpageCategoriesJSON(main_page_id):
    main_page = session.query(MainPage).filter_by(id=main_page_id).one()
    items = session.query(Categories).filter_by(
        main_page_id=main_page_id).all()
    return jsonify(Categories=[i.serialize for i in items])



# JSON Endpoint   
@app.route('/frenchyfabric/<int:main_page_id>/category/<int:categories_id>/JSON')
def CategoryItemJSON(main_page_id, categories_id):
    CategoryItem = session.query(Categories).filter_by(id=categories_id).one()
    return jsonify(CategoryItem=CategoryItem.serialize) 



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
