from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm, LoginForm, UpdateForm
from datetime import datetime
import json
import RPi.GPIO as GPIO
from bs4 import BeautifulSoup as soup
import requests
import lxml
from flask_sqlalchemy import SQLAlchemy   

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a52c251cf3c7cef9327f6202007df737'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

posts = [
    {
        'author': 'Aki Isokangas',
        'title': 'Blog Post -13042020- ',
        'content': 'Lisätty muuttujien päivitys "Modify"-linkin taakse.\
                    Lisätty Teho yläpalkkiin.\
                    Lisätty Virheentarkistus teholle',
        'date_posted': 'April 13, 2020'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

MYDICT = {
    "varfile": '/home/pi/steca/variables.json',
    "varfile1": '/home/pi/steca/power.json',
    "power": '',
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
MYDICT["start"] = int(variables["start"])
MYDICT["stop"] = int(variables["stop"])

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   26 : {'name' : 'Water Heater', 'state' : GPIO.LOW},
   20 : {'name' : 'Rele 2', 'state' : GPIO.LOW},
   21 : {'name' : 'Rele 3', 'state' : GPIO.LOW}
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
def modify():
    hae_teho_from_file()
    form = UpdateForm()
    reload_vars()
    #if request.method == 'POST' and form.validate_on_submit():
    if form.validate_on_submit():
        if request.method == 'POST':
            MYDICT["power"] = form.power.data
            MYDICT["start"] = form.start.data
            MYDICT["stop"] = form.stop.data
            my_data = {
                "power": MYDICT["power"],
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
       'start' : MYDICT["start"], 
       'stop' : stop
       }
    return render_template('modify.html', title='Modify', form=form, teho=MYDICT["teho"], **templateData)

@app.route("/login", methods=['GET', 'POST'])
def login():
    hae_teho_from_file()
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form, teho=MYDICT["teho"])

@app.route("/about")
def about():
    hae_teho_from_file()
    return render_template('about.html', teho=MYDICT["teho"], title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        #flash(f'Account created for {form.username.data}!', 'success')
        flash('Account created')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form, teho=MYDICT["teho"])

def reload_vars():
    ''''
    Reload power, start and stoptimes from variables.json file
    '''
    with open(MYDICT["varfile"]) as f:
        variables = json.load(f)
    MYDICT["power"] = int(variables['power'])
    MYDICT["start"] = int(variables['start'])
    MYDICT["stop"] = int(variables['stop'])

def update_vars():
    ''''
    Reload power, start and stoptimes from variables.json file
    '''
    data = {}
    data['power']
    data['power']
    data['power']
    with open(MYDICT["varfile"], 'w') as f:
        json.dump(data, f)
        close(f)
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

if __name__ == '__main__':
   app.run(host="192.168.10.53", port=80, debug=True)
