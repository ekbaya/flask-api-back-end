
#
# Elias Baya <eliasbaya1223@gmail.com>
# @version		1.0
# @copyright	Copyright (C)
#  @license		GNU General Public License version 2 or later; see LICENSE.txt

from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from flask import jsonify
from flask_bcrypt import Bcrypt
from passlib.hash import sha256_crypt
import datetime



app = Flask(__name__)

bcrypt = Bcrypt(app)

# Secret key (can be anything, it's for extra protection)
app.secret_key = 'd6bf0a5f-9c2e-494d-84e1-d347a8466931'

# Database connection details
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mysql'

app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/admin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
     # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # password = sha256_crypt.encrypt(request.form['password'])

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s AND password = %s', (email, password,))
        # Fetch one record and return result
        account = cursor.fetchone()

          # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['user_id']
            session['email'] = account['email']
            session['firstname'] = account['firstname']
            session['lastname'] = account['lastname']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect email/password!'
    return render_template('main/pages/accounts/login.html', msg=msg)


# http://localhost:5000/admin/logout - this will be the logout page
@app.route('/admin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('email', None)
   session.pop('firstname', None)
   session.pop('lastname', None)
   # Redirect to login page
   return redirect(url_for('login'))


# http://localhost:5000/admin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/admin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "firstname", "lastname" ,"email" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = sha256_crypt.encrypt(request.form['password'])

          # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))

        # If account exists show error and validation checks
        if cursor.fetchone():
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not firstname or not lastname or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (%s, %s, %s, %s, %s)', (None, firstname, lastname, email, password,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('main/pages/accounts/register.html', msg=msg)


# http://localhost:5000/admin/ - this will be the home page, only accessible for loggedin users
@app.route('/admin/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('main/home.html', email=session['email'], firstname=session['firstname'], lastname=session['lastname'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Errors definations
def error_403():
    return render_template('main/errors/403.html')

def error_404():
    return render_template('main/errors/404.html')

def error_500():
    return render_template('main/errors/500.html')

def error_505():
    return render_template('main/errors/505.html')

# Error listeners
@app.errorhandler(403)
def error403(error=None):
    message = {
        'status': 403,
        'message': 'The request was valid, but the server is refusing action. You might not have the necessary permissions for a resource, or may need an account of some sort',
    }
    resp = jsonify(message)
    resp.status_code = 403

    return resp and error_403()

@app.errorhandler(404)
def error404(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp and error_404()

@app.errorhandler(500)
def error500(error=None):
    message = {
        'status': 500,
        'message': 'Unexpected condition was encountered and no more specific message is suitable.',
    }
    resp = jsonify(message)
    resp.status_code = 500

    return resp and error_500()

@app.errorhandler(505)
def error505(error=None):
    message = {
        'status': 505,
        'message': 'The server does not support the HTTP protocol version used in the request.',
    }
    resp = jsonify(message)
    resp.status_code = 505

    return resp and error_505()



# http://localhost:5000/admin/sickTraces- this will open tables page
@app.route('/admin/sickTraces')
def sickTraces():
    return render_template('main/pages/sick/traces.html')


@app.route('/addlocation/', methods=['POST'])
def addlocation():
    try:
        data = request.get_json(force=True)
        device = data['device']
        latitude = data['latitude']
        longitude = data['longitude']
        time_stamp = data['time_stamp']

        if device and latitude and longitude and time_stamp and request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO locations VALUES (%s, %s, %s, %s)', (device, latitude, longitude, time_stamp,))
            mysql.connection.commit()
            resp = {'message':'Location added successifully', 'status_code': 200}
            return jsonify(resp)
        else:
            return error404()
    except Exception as e:
           print(e)
           return error404()
    return error404()


@app.route('/addUser/', methods=['GET','POST'])
def addUser():
    try:
        data = request.get_json(force=True)
        email = data['email']
        password = data['password']

        if email and password and request.method == 'POST':
             # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))

            # If account exists show error and validation checks
            if not cursor.fetchone():
                # Account doesnt exists and the form data is valid, now insert new account into accounts table

                pw_hash = bcrypt.generate_password_hash(password)

                now = datetime.datetime.now()
                date = now.strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s)', (email, pw_hash, date,))
                mysql.connection.commit()
                resp = {'message':'You have successfully registered!', 'status_code':201, 'success':'true',
                'data': {'email': email}}
                return jsonify(resp)
            else:
                resp = {'message':'Email is already registered ', 'status_code': 200, 'success':'false',
                'data': {'email':'No email registered'}}
                return jsonify(resp)

        else:
            return error404()
    except Exception as e:
           print(e)
           return error404()
    return error404()


@app.route('/loginUser/', methods=['GET','POST'])
def loginUser():
    try:
        data = request.get_json(force=True)
        email = data['email']
        password = data['password']

        if email and password and request.method == 'POST':
             # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))

            # If account exists show error and validation checks
            if not cursor.fetchone():
                # Account doesnt exists
                resp = {'message':'The email u have entered is not registered', 'status_code':200, 'success':'false',
                'data': {'email': 'email is not registered'}}
                return jsonify(resp)
            else:
                cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                result_row = cursor.fetchone()
                pw_hash = result_row['password']

                if bcrypt.check_password_hash(pw_hash, password):
                    resp = {'message':'Logged in successfully', 'status_code': 200, 'success':'true',
                    'data': {'email': email}}
                    return jsonify(resp)
                else:
                    resp = {'message':'Invalid email or password ', 'status_code': 200, 'success':'false',
                    'data': {'email':'No email registered'}}
                    return jsonify(resp)
        else:
            return error404()
    except Exception as e:
           print(e)
           return error404()
    return error404()

@app.route('/users/', methods=['GET','POST'])
def users():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT user_id, email, date_created FROM users')

        data = cursor.fetchall()
        return render_template('main/pages/tables/users-table.html', data=data)
    except Exception as e:
        print(e)
        return error_500()

@app.route('/admins/', methods=['GET','POST'])
def admins():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT user_id, firstname, lastname, email FROM accounts')

        data = cursor.fetchall()
        return render_template('main/pages/tables/admins-table.html', data=data)
    except Exception as e:
        print(e)
        return error_500()

locations = []

# http://localhost:5000/search/<device>'/
@app.route('/search/', methods=['GET','POST'])
def search():
     # Output message if something goes wrong...
    msg = ''
     # Check if "email" and POST requests exist (user submitted form)
    if request.method == 'POST' and 'device' in request.form:
        # Create variables for easy access
        device = request.form['device']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT latitude, longitude, time_stamp FROM locations WHERE device = %s', (device,))
        locations_history = cursor.fetchall()

        if locations_history:
            msg = 'Locations fetched succesifully'
            for row in locations_history:
                list1 = [float(row['latitude']),float(row['longitude']),float(row['time_stamp'])]
                locations.append(list1)
            return save_sick_traces(locations)
        else:
            msg = 'No location history for the device , check and try again'
    return render_template('main/pages/sick/traces.html', msg=msg)




# http://localhost:5000/save/ - this will be called to execute saving of a new sick trace in the data folder
@app.route('/save/')
def save_sick_traces(locations):
     # Output message if something goes wrong...
     msg = ''
     n = len(os.listdir("data"))
     with open("data/"+ str(n+1) + ".json", 'w') as f:
        json.dump(locations, f)
        msg = 'Locations added succesifully'
        return render_template('main/pages/sick/traces.html', msg=msg)

sick_traces = []

def load_sick_traces():
    n = len(os.listdir("mysite/data"))
    for i in range(1, n+1):
        with open("mysite/data/" + str(i) + ".json") as f:
            sick_traces.append(json.load(f))


# http://heartbeat/<offset>/
@app.route('/heartbeat/<offset>')
def heartbeat(offset):
    load_sick_traces()
    offset = int(offset)
    if offset >= 0 and offset < len(sick_traces):
        return json.dumps(sick_traces[offset:])
    return json.dumps([])


if __name__ == '__main__':
    load_sick_traces()
    app.run()
