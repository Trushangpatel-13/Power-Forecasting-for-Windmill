
import pyrebase
from datetime import datetime
import requests

firebaseConfig = {
  "apiKey": "AIzaSyAN8oJ03k5oB9NsAa9hg65Xnp2vRO_U9BQ",
  "authDomain": "wind-data-logger.firebaseapp.com",
  "databaseURL": "https://wind-data-logger-default-rtdb.firebaseio.com",
  "projectId": "wind-data-logger",
  "storageBucket": "wind-data-logger.appspot.com",
  "messagingSenderId": "954988157014",
  "appId": "1:954988157014:web:270bcd30522ed382e043f7",
  "measurementId": "G-NST6ZZ7CV9"
}

api_key = "a4090eff80166f366f980227d8292fcf"
lat = 22.3072
lon = 73.1812
data = {}
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
base = "http://api.openweathermap.org/data/2.5/weather?lat="
url = base + str(lat) + "&lon=" + str(lon) + "&appid=" + api_key
print(url)
x = requests.get(url).json()
data["temp"] = x["main"]["temp"]
data["pressure"] = x["main"]["pressure"]
data["humidity"] = x["main"]["humidity"]
data["temp_max"] = x["main"]["temp_max"]
data["temp_min"] = x["main"]["temp_min"]

data["wind_speed"] = x["wind"]["speed"]
data["wind_deg"] = x["wind"]["deg"]
data["Date"] = x["dt"]

now = datetime.now()
#print("now =", now)
# dd/mm/YY H:M:S
dt_string = now.strftime("%d-%m-%Y_%H:%M:%S")
#print("date and time =", dt_string)

db.child(dt_string).set(data)
#print(data)

