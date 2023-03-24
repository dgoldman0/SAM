import os
import requests
import json

token = os.environ.get("news_key")

def search(args):
    function_args = json.loads(args)

    q = function_args.get('query')
    since = function_args.get('since')
    until = function_args.get('until')
    page_size = function_args.get('page_size')
    sort = function_args.get('sort')

    if page_size is None:
        page_size = "10"

    url = "https://newsapi.org/v2/everything?q=" + q
    if since is not None:
         url += "&from=" + since
    if until is not None:
        url += "&to=" + until
    url += "&pageSize=" + str(page_size)
    if sort is not None:
        url += "&sortBy=" + sort
    url += "&apiKey=" + token

    response = requests.get(url)

    data = response.json()

    if data["status"] == "ok":
        return str(data["articles"])
    else:
        return "Error getting news from News API"