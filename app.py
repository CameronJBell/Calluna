from flask import Flask, render_template, redirect, request, jsonify
from dotenv import load_dotenv
import os
import requests
from supabase import create_client

load_dotenv()
app = Flask(__name__)

# Initialise supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# Setup WeatherAPI API details
weatherapi_url = os.environ.get("WEATHERAPI_URL")
weatherapi_key = os.environ.get("WEATHERAPI_KEY")
# Setup OpenWeatherMap API details
owm_geo_url = os.environ.get("OPENWEATHERMAP_GEO_URL") # Geocoding API
owm_key = os.environ.get("OPENWEATHERMAP_KEY")

def get_city_coordinates(city):
    # Don't waste API requests on hard-coded locations
    match city:
        case "Berlin":
            return 52.5170365, 13.3888599
        case "London":
            return 51.5073219, -0.1276474
        case "Los Angeles":
            return 34.0536909, -118.242766
        case "New York":
            return 40.7127281, -74.0060152
        case "Tokyo":
            return 35.6828387, 139.7594549
        case _:
            # Get coordinates from API
            #query = f"{owm_geo_url}?q={city}&limit=1&appid={owm_key}"
            params = {
                    "q": city,
                    "limit": 1,
                    "appid": owm_key
                    }
            res = requests.get(owm_geo_url, params=params).json()
            return res[0]["lat"], res[0]["lon"]


def get_current_weather_data(lat, long):
    # Fetch from API
    #query = f"{weatherapi_url}/current.json?q={lat},{long}&key={weatherapi_key}"
    params = {
            "q": f"{lat},{long}",
            "key": weatherapi_key
            }
    res = requests.get(weatherapi_url + "/current.json", params=params).json()

    """
    weather = {
            "city": res["location"]["name"],
            "temperature": res["current"]["temp_c"],
            "wind": {
                "speed": res["current"]["wind_mph"],
                "direction": res["current"]["wind_dir"]
                },
            "condition": {
                "text": res["current"]["condition"]["text"],
                "icon": "https://" + str(res["current"]["condition"]["icon"])
                }
            }
    """
    weather = {
            "city": "London",
            "temperature": 17.9,
            "wind": {
                "speed": 6.7,
                "direction": "ESE"
                },
            "condition": {
                "text": "Sunny",
                "icon": "https:" + "//cdn.weatherapi.com/weather/64x64/day/116.png"
                }
            }
    return weather

@app.route("/")
def index():
    cities = []
    weather_data = []

    if supabase.auth.get_user():
        cities = []
    else:
        cities.extend(["Berlin", "London", "Los Angeles", "New York", "Tokyo"])

    for city in cities:
        latitude, longitude = get_city_coordinates(city)
        data = get_current_weather_data(latitude, longitude)
        weather_data.append(data)

    return render_template("index.html", weather_data=weather_data)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # TODO: Create new user
        return redirect("/login")
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # TODO: Set auth code -- supabase?
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    # TODO: Logout code
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
