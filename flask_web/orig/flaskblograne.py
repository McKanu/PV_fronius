from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm, LoginForm, UpdateRaneForm
from datetime import datetime
import json
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a52c251cf3c7cef9327f6202007df737'

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

MYDICT = {
    "varfile": '/home/pi/steca/variables_all.json',
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

MYDICT["power"] = int(variables["power"])
MYDICT["power1"] = int(variables["power1"])
MYDICT["power2"] = int(variables["power2"])
MYDICT["power3"] = int(variables["power3"])
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
#   GPIO.setup(pin, GPIO.OUT)

def read_state():
    # Read current state for each pins
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        pins[pin]['state'] = GPIO.input(pin)
        print(pins[pin]['state'])

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

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

   return render_template('manual.html', **templateData)

@app.route("/manual")
def manual():
   # For each pin, read the pin state and store it in the pins dictionary:
   read_state()
   # Put the pin dictionary into the template data dictionary:
   templateData = {
      'pins' : pins
      }
   # Pass the template data into the template main.html and return it to the user
   return render_template('manual.html', title='Manual Rele Control', **templateData)

@app.route("/modify", methods=['GET', 'POST'])
def modify():
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
    return render_template('modify_rane.html', title='Modify', form=form, **templateData)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        #flash(f'Account created for {form.username.data}!', 'success')
        flash('Account created')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

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

if __name__ == '__main__':
    app.run(host="192.168.10.53", port=80, debug=True)
