from flask import Flask, render_template, redirect, request, jsonify
from dotenv import load_dotenv
import base64
import bleach
import os
import requests
import matplotlib.pyplot as plt
import pandas
from supabase import create_client
from io import BytesIO

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
            params = {
                    "q": city,
                    "limit": 1,
                    "appid": owm_key
                    }
            res = requests.get(owm_geo_url, params=params).json()
            return res[0]["lat"], res[0]["lon"]


def get_current_weather_data(lat, long):
    # Fetch from API
    params = {
            "q": f"{lat},{long}",
            "key": weatherapi_key
            }
    res = requests.get(weatherapi_url + "/current.json", params=params).json()

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
    return weather

def get_forecast(lat, long):
    params = {
            "q": f"{lat},{long}",
            "days": 7,
            "key": weatherapi_key
            }
    return requests.get(weatherapi_url + "/forecast.json", params=params).json()

def create_forecast_charts(weather_data):
    weather_charts = {}
    # Daily Forecast
    dates = []
    daily_temps = []
    daily_chance_rain = []
    for data in weather_data["forecast"]["forecastday"]:
        dates.append(data["date"])
        daily_temps.append(data["day"]["avgtemp_c"])
        daily_chance_rain.append(data["day"]["daily_chance_of_rain"])

    plot_data = pandas.DataFrame({"Date": dates, "Avg Temp": daily_temps, "Rain": daily_chance_rain})

    ax = plot_data.plot.bar(x="Date", y="Avg Temp", ylabel=u"Temperature (\u2103)", xlabel="Date", color="red")
    ax2 = ax.twinx()
    plot_data.plot(x="Date", y="Rain", marker="o", color="blue", ylabel="Chance of rain (%)", ax=ax2)
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")
    buf = BytesIO()
    ax2.figure.autofmt_xdate()
    ax2.figure.savefig(buf, format="png")
    daily_forecast_plot_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    
    weather_charts.update({"daily_forecast": daily_forecast_plot_data})
    return weather_charts

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


@app.route("/search", methods=["POST"])
def search():
    search = bleach.clean(request.form["search"])
    params = {
            "q": search,
            "limit": 10,
            "appid": owm_key
            }
    if search: # Don't send API request for empty search
        search_data = requests.get(owm_geo_url, params=params).json()

    return render_template("search.html", search_data=search_data)

@app.route("/weather", methods=["GET"])
def display_weather():
    lat = bleach.clean(request.args.get("lat"))
    long = bleach.clean(request.args.get("long"))

    weather_data = get_forecast(lat, long)
    weather_charts = create_forecast_charts(weather_data)

    return render_template("weather.html", weather_data=weather_data,
                           weather_charts=weather_charts)

if __name__ == "__main__":
    app.run(debug=True)
