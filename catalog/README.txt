
## Frenchy Fabric Item Catalog
Built on Flask and SQLite.

## Objection
To Develop a modern web application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Rescources
  * [Vagrant](https://www.vagrantup.com/)
  * [VirtualBox](https://www.virtualbox.org/)
  * [Flask](http://flask.pocoo.org)
  * [SQLAlchemy](http://www.sqlalchemy.org)

## Quickstart
1. Git clone the repository and cd into it.
2. If you haven't already, [install pip](https://pip.pypa.io/en/stable/installing/).
3. (Optional) Install virtualenv and activate the virtual environment. `pip install virtualenv` `virtualenv ENV` `source ENV/bin/activate`
4. Install the dependencies. `pip install -r requirements.txt`
5. Setup the database. `python database_setup.py`
6. Populate the database.  `python fabricfabric.py`
7. Run the app. `python application.py`

## Usage
* Login by clicking the 'Login' link and logging in via Google
* Once logged in, you will see view, edit, and delete buttons beside each item row in the catalog
* To view the JSON output, go to `/frenchyfabric/JSON` or `/frenchyfabric/<int:merchandise_id>/category/JSON`