import datetime
import time
import RPi.GPIO as GPIO
import logging

from flask import Flask, render_template, request
from flask_httpauth import HTTPBasicAuth
from time import strftime
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
auth = HTTPBasicAuth()

GPIO.setmode(GPIO.BCM)
garage1 = 27
garagepin = 4
GPIO.setup(garage1, GPIO.IN, GPIO.PUD_UP )

users = {
    "me": "abc123",
}

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

def term():
    GPIO.cleanup()

@app.route('/')
@auth.login_required
def hello():
   now = datetime.datetime.now()
   timeString = now.strftime("%d-%m-%Y %H:%M:%S")
   templateData = {
      'title' : 'HELLO!',
      'time': timeString
      }
   return render_template('index.html', **templateData)

@app.route('/garage')
@auth.login_required
def main():
   state = GPIO.input(garage1)
   templateData = { 'name' : 'Garage', 'state' : state }
   return render_template('main.html', **templateData) 

@app.route('/garage/<action>')
def action(action):
   if action == "open":
      GPIO.setup(garagepin, GPIO.OUT, initial=GPIO.HIGH)
      GPIO.output(garagepin, GPIO.LOW)
      time.sleep( 0.5 )
      GPIO.output(garagepin, GPIO.HIGH)
      message = "Opened garage"

   if action == "close":
      GPIO.setup(garagepin, GPIO.OUT, initial=GPIO.HIGH)
      GPIO.output(garagepin, GPIO.LOW)
      time.sleep( 0.5 )
      GPIO.output(garagepin, GPIO.HIGH)
      message = "Closing garage"

   templateData = {
      'message' : message,
   }

   return render_template('main.html', **templateData)


@app.after_request
def after_request(response):
    timestamp = strftime('[%d-%m-%Y %H:%M:%S]')
    logger.error('%s %s %s %s %s %s', 
        timestamp, request.remote_addr,request.method, 
        request.scheme, request.full_path, response.status)
    return response

if __name__ == "__main__":
   handler = RotatingFileHandler('/var/log/api/app.log', maxBytes=100000, backupCount=3)
   logger = logging.getLogger('tdm')
   logger.setLevel(logging.ERROR)
   logger.addHandler(handler)
   app.run(host='0.0.0.0', port=5000, threaded=True,  debug=True)
