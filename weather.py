from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
import os

token = os.environ.get("weather_key")
owm = OWM(token)
mgr = owm.weather_manager()

def currentWeather(lat, lon):
    global mgr
    one_call = mgr.one_call(lat=lat, lon=lon, units = "metric")
    w = one_call.current
    return str({'detailed_status': w.detailed_status, 'wind': str(w.wind()), 'humidity': w.humidity, 'temp': str(w.temperature()), 'rain': w.rain, 'snow': w.snow, 'heat_index': w.heat_index, 'clouds': w.clouds})

def sevenDay(lat, lon):
    global mgr
    one_call = mgr.one_call(lat=lat, lon=lon, units = "metric")
    forecast = ""
    for day in range(0, 8):
        w = one_call.forecast_daily[day]
        forecast += "Day " + str(day) + ": " + str({'detailed_status': w.detailed_status, 'wind': str(w.wind()), 'humidity': w.humidity, 'temp': str(w.temperature()), 'rain': w.rain, 'snow': w.snow, 'heat_index': w.heat_index, 'clouds': w.clouds}) + "\n"
    return forecast
