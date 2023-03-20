from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
import os

# ---------- FREE API KEY examples ---------------------
token = os.environ.get("weather_key")
owm = OWM(token)
mgr = owm.weather_manager()

def currentWeather(lat, lon):
    one_call = mgr.one_call(lat=lat, lon=lon, units = "metric")
    w = one_call.current
    return str({'detailed_status': w.detailed_status, 'wind': str(w.wind()), 'humidity': w.humidity, 'temp': str(w.temperature()), 'rain': w.rain, 'snow': w.snow, 'heat_index': w.heat_index, 'clouds': w.clouds})
