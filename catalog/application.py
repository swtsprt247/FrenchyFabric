from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Merchandise, Base, Categories, User
from functools import wraps

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

engine = create_engine('sqlite:///frenchy_fabric.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def login():
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
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
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
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
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
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

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
                   'email'])
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
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # If the given token was invalid notice the user.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'username' in login_session:
        gdisconnect()
        flash("You have successfully been logged out.")
        return redirect(url_for('showMerchandise'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showMerchandise'))


# Login Required function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not logged in, Please login to continue...")
            return redirect('/login')
    return decorated_function




# Show all merchandise
@app.route('/')
@app.route('/frenchyfabric/')
def showMerchandise():
    merchandises = session.query(Merchandise).order_by(asc(Merchandise.name))
    if 'username' not in login_session:
        return render_template('publicMerchandise.html', merchandises=merchandises)
    else:
        return render_template('merchandise.html', merchandises=merchandises)


# Create a new merchandise
@app.route('/frenchyfabric/new/', methods=['GET', 'POST'])
@login_required
def newMerchandise():    
    if request.method == 'POST':
        newMerchandise = Merchandise(name=request.form['name'])
        session.add(newMerchandise)
        flash('New Merchandise %s Successfully Created' % newMerchandise.name)
        session.commit()
        return redirect(url_for('showMerchandise'))
    else:
        return render_template('newMerchandise.html')


@app.route('/frenchyfabric/<int:merchandise_id>/edit/', methods=['GET', 'POST'])
@login_required
def editMerchandise(merchandise_id):
    editedMerchandise = session.query(Merchandise).filter_by(id=merchandise_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedMerchandise.name = request.form['name']
            flash('Merchandise Successfully Edited %s' % editedMerchandise.name)
            return redirect(url_for('showMerchandise'))
    else:
        return render_template('editMerchandise.html', merchandise=editedMerchandise)


# Delete a Merchandise
@app.route('/frenchyfabric/<int:merchandise_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteMerchandise(merchandise_id):
    merchandiseToDelete = session.query(
        Merchandise).filter_by(id=merchandise_id).one()
    if request.method == 'POST':
        session.delete(merchandiseToDelete)
        flash('%s Successfully Deleted' % merchandiseToDelete.name)
        session.commit()
        return redirect(url_for('showMerchandise', merchandise_id=merchandise_id))
    else:
        return render_template('deleteMerchandise.html', merchandise=merchandiseToDelete)


# Show items inside the category
@app.route('/frenchyfabric/<int:merchandise_id>/')
@app.route('/frenchyfabric/<int:merchandise_id>/category/')
@login_required
def showCategories(merchandise_id):
    merchandise = session.query(Merchandise).filter_by(id=merchandise_id).one()
    items = session.query(Categories).filter_by(merchandise_id=merchandise_id).all()
    if 'username' not in login_session:
        return render_template('publicCategories.html', items=items, merchandise=merchandise)
    else:
        return render_template('categories.html', items=items, merchandise=merchandise)


# Route for new Merchandise categories
@app.route('/frenchyfabric/<int:merchandise_id>/new', methods=['GET', 'POST'])
@login_required
def newCategoryItem(merchandise_id):
    merchandise = session.query(Merchandise).filter_by(id=merchandise_id).one()
    if 'username' not in login_session:
        if request.method == 'POST':
            newItem = Categories(
                name=request.form['name'], description=request.form['description'], merchandise_id=merchandise_id)
            session.add(newItem)
            session.commit()
            flash('New Category %s Item Successfully Created' % (newItem.name))
            return redirect(url_for('showCategories', merchandise_id=merchandise_id))
    else:
        return render_template('NewCategoryItem.html', merchandise_id=merchandise_id)


# Route to edit categories
@app.route('/frenchyfabric/<int:merchandise_id>/<int:categories_id>/edit/', methods=['GET', 'POST'])
@login_required
def editCategoryItem(merchandise_id, categories_id):
    editedItem = session.query(Categories).filter_by(id=categories_id).one()
    merchandise = session.query(Merchandise).filter_by(id=merchandise_id).one()
    if 'username' not in login_session:
        if request.method == 'POST':
            if request.form['name']:
                editedItem.name = request.form['name']
            if request.form['description']:
                editedItem.description = request.form['description']
                session.add(editedItem)
                session.commit()
                flash("Category has been edited!")
                return redirect(url_for('showCategories', merchandise_id=merchandise_id))
            else:
                return render_template('EditCategoryItem.html', merchandise_id=merchandise_id, categories_id=categories_id, i=editedItem)


# Route to delete categories
@app.route('/frenchyfabric/<int:merchandise_id>/<int:categories_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategoryItem(merchandise_id, categories_id):
    itemToDelete = session.query(Categories).filter_by(id=categories_id).one()
    merchandise = session.query(Merchandise).filter_by(id=merchandise_id).one()
    if 'username' not in login_session:
        if request.method == 'POST':
            session.delete(itemToDelete)
            session.commit()
            flash("Category has been deleted!")
            return redirect(url_for('showCategories', merchandise_id=merchandise_id))
        else:
            return render_template('DeleteCategoryItem.html', i=itemToDelete)


# Making an API Endpoint (GET Request)
@app.route('/frenchyfabric/<int:merchandise_id>/category/JSON')
def MerchandiseCategoriesJSON(merchandise_id):
    merchandise = session.query(Merchandise).filter_by(id=merchandise_id).one()
    items = session.query(Categories).filter_by(
        merchandise_id=merchandise_id).all()
    return jsonify(Categories=[i.serialize for i in items])


# JSON Endpoint
@app.route('/frenchyfabric/JSON')
def MerchandiseJSON():
    merchandise = session.query(Merchandise).all()
    return jsonify(merchandise=[r.serialize for r in merchandise])

# @app.route('/frenchyfabric/<int:merchandise_id>/category/<int:categories_id>/JSON')
# def CategoryItemJSON(merchandise_id, categories_id):
#     CategoryItem = session.query(Categories).filter_by(id=categories_id).one()
#     return jsonify(CategoryItem=CategoryItem.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
