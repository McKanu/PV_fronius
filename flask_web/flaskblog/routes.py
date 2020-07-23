import os
import secrets
from PIL import Image
from flaskblog import app, db, bcrypt
from flaskblog.models import User, Post
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, UpdateRaneForm
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
import json
import RPi.GPIO as GPIO
from bs4 import BeautifulSoup as soup
import requests
import lxml
from flask_sqlalchemy import SQLAlchemy   

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

posts = [
    {
        'author': 'Aki Isokangas',
        'title': 'Info',
        'content': 'Muuttujien automaattinen lataus ei näytä toimivan vielä',
        'date_posted': 'April 28, 2020'
    },
    {
        'author': 'Aki Isokangas',
        'title': 'Blog Post 28042020',
        'content': 'Lisätty ohjaus kaikille kolmelle releelle tänään',
        'date_posted': 'April 28, 2020'
    },
    {
        'author': 'Aki Isokangas',
        'title': 'Blog Post 13042020',
        'content': 'Lisätty muuttujien päivitys "Modify"-linkin taakse.\
                    Lisätty Teho yläpalkkiin.\
                    Lisätty Virheentarkistus teholle',
        'date_posted': 'April 13, 2020'
    }
]

MYDICT = {
    "varfile": '/home/pi/steca/variables.json',
    "varfile1": '/home/pi/steca/power.json',
    "power": '',
    "power1": '',
    "power2": '',
    "power3": '',
    "teho": '' ,
    "power": '',
    "start": '',
    "stop": ''
}

with open(MYDICT["varfile"]) as f:
    variables = json.load(f)
with open(MYDICT["varfile1"]) as f1:
    varfile1 = json.load(f1)

MYDICT["power"] = int(variables["power"])
MYDICT["power1"] = int(variables["power1"])
MYDICT["power2"] = int(variables["power2"])
MYDICT["power3"] = int(variables["power3"])
MYDICT["start"] = int(variables["start"])
MYDICT["stop"] = int(variables["stop"])

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   26 : {'name' : 'Rele1', 'state' : GPIO.LOW},
   20 : {'name' : 'Rele2', 'state' : GPIO.LOW},
   21 : {'name' : 'Rele3', 'state' : GPIO.LOW}
   }

# Setup each pins
#for pin in pins:


def read_state():
    # Read current state for each pins
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        pins[pin]['state'] = GPIO.input(pin)
        print(pins[pin]['state'])

@app.route("/")
@app.route("/home")
def home():
    #hae_teho()
    hae_teho_from_file()
#    templateData = {
#       'teho' : MYDICT["teho"]
#    }

    return render_template('home.html', posts=posts, teho=MYDICT["teho"])

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<changePin>/<action>")
@login_required
def action(changePin, action):
   # Convert the pin from the URL into an integer:
   changePin = int(changePin)
   # Get the device name for the pin being changed:
   deviceName = pins[changePin]['name']
   # If the action part of the URL is "on," execute the code indented below:
   if action == "on":
      # Set the pin high:
      GPIO.output(changePin, GPIO.HIGH)
      # Save the status message to be passed into the template:
      message = "Turned " + deviceName + " off."
   if action == "off":
      GPIO.output(changePin, GPIO.LOW)
      message = "Turned " + deviceName + " on."
   if action == "toggle":
      # Read the pin and set it to whatever it isn't (that is, toggle it):
      GPIO.output(changePin, not GPIO.input(changePin))
      message = "Toggled " + deviceName + "."

   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)

   # Along with the pin dictionary, put the message into the template data dictionary:
   templateData = {
      'message' : message,
      'pins' : pins
   }

   return render_template('manual.html', teho=MYDICT["teho"], **templateData)

@app.route("/manual")
@login_required
def manual():
   hae_teho_from_file()
   # For each pin, read the pin state and store it in the pins dictionary:
   read_state()
   # Put the pin dictionary into the template data dictionary:
   templateData = {
      'pins' : pins
      }
   # Pass the template data into the template main.html and return it to the user
   return render_template('manual.html', title='Manual Rele Control', teho=MYDICT["teho"], **templateData)

@app.route("/modify", methods=['GET', 'POST'])
@login_required
def modify():
    hae_teho_from_file()
    # Aki: form = UpdateForm()
    # Rane: form = UpdateRaneForm()
    form = UpdateRaneForm()
    reload_vars()
    #if request.method == 'POST' and form.validate_on_submit():
    if form.validate_on_submit():
        if request.method == 'POST':
            MYDICT["power"] = form.power.data
            MYDICT["power1"] = form.power1.data
            MYDICT["power2"] = form.power2.data
            MYDICT["power3"] = form.power3.data
            MYDICT["start"] = form.start.data
            MYDICT["stop"] = form.stop.data
            my_data = {
                "power": MYDICT["power"],
                "power1": MYDICT["power1"],
                "power2": MYDICT["power2"],
                "power3": MYDICT["power3"],
                "start": MYDICT["start"],
                "stop": MYDICT["stop"]
                }
            with open(MYDICT["varfile"], 'w') as f:
                json.dump(my_data, f, indent=4)
                f.close()
            flash('Parameters has been updated', 'success')
            return redirect(url_for('home'))
        else:
            flash('Failed to update variables.json file', 'danger')
            return redirect(url_for('home'))
    message = "Nykyiset arvot:"
    stop = MYDICT["stop"]+1
    templateData = {
       'message' : message,
       'power' : MYDICT["power"], 
       'power1' : MYDICT["power1"], 
       'power2' : MYDICT["power2"], 
       'power3' : MYDICT["power3"], 
       'start' : MYDICT["start"], 
       'stop' : stop
       }
    return render_template('modify.html', title='Modify', form=form, teho=MYDICT["teho"], **templateData)
    #return render_template('modify.html', title='Modify', form=form, teho=MYDICT["teho"])

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    hae_teho_from_file()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form, teho=MYDICT["teho"])

@app.route("/about")
def about():
    hae_teho_from_file()
    return render_template('about.html', teho=MYDICT["teho"], title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        print(hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, teho=MYDICT["teho"])

def reload_vars():
    ''''
    Reload power, start and stoptimes from variables.json file
    '''
    with open(MYDICT["varfile"]) as f:
        variables = json.load(f)
    MYDICT["power"] = int(variables['power'])
    MYDICT["power1"] = int(variables['power1'])
    MYDICT["power2"] = int(variables['power2'])
    MYDICT["power3"] = int(variables['power3'])
    MYDICT["start"] = int(variables['start'])
    MYDICT["stop"] = int(variables['stop'])

#def update_vars():
#    ''''
#    Reload power, start and stoptimes from variables.json file
#    '''
#    data = {}
#    data['power']
#    data['power']
#    data['power']
#    with open(MYDICT["varfile"], 'w') as f:
#        json.dump(data, f)
#        close(f)
def read_ac_power(data):
    ''''
    https://stackoverflow.com/questions/59802202/python-3-xml-data-to-variables
    '''
    variable=soup(data,'lxml')
    val=variable.findAll('measurement')[6]
    if val.get('value') == None:
        return 0
    else:
        return val['value']
def hae_teho():
    ''''
    Fetch XML-data from Steca inverter and change String-to-Float using read_ac_power-function
    '''
    r = requests.get('http://192.168.10.59/measurements.xml')
    MYDICT['teho'] = round(float(read_ac_power(r.text)))

def hae_teho_from_file():
    ''''
    Fetch XML-data from Steca inverter and change String-to-Float using read_ac_power-function
    '''
    with open(MYDICT["varfile1"]) as f1:
        varfile1 = json.load(f1)
    MYDICT['teho'] = varfile1["teho"]
@app.route("/logout")
def logout():
    logout_user() 
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form, teho=MYDICT["teho"])

