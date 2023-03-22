import os
import requests
import json

token = os.environ.get("yelp_key")

def search(term, lat, lon):
    url = "https://api.yelp.com/v3/businesses/search?term=" + term + "&latitude=" + lat + "&longitude=" + lon + "&limit=5&radius=10000"
    response = requests.get(url = url, headers = {"Authorization": "Bearer " + token, "accept": "application/json"})
    data = response.json()
    return str(data)
