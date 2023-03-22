import tweepy
import os
import json

token = os.environ.get("twitter_bearer_key")
client_id = os.environ.get("twitter_client_id")
client_secret = os.environ.get("twitter_client_secret")

def search(args):
    global token
    try:
        client = tweepy.Client(bearer_token=token)
        function_args = json.loads(args)
        query = function_args.get("query")
        next_token = function_args.get("last)")
        max_results=function_args.get("max_results")
        tweets = client.search_recent_tweets(query=query, tweet_fields=['context_annotations', 'created_at', 'conversation_id'],
                                             user_fields=['name'], expansions='author_id', max_results=max_results, next_token=next_token)

        # Get users list from the includes object
        users = {u["id"]: u for u in tweets.includes['users']}
        results = []
        for tweet in tweets.data:
            if users[tweet.author_id]:
                user = users[tweet.author_id]
                results.append({'from':user.name, 'from_id':str(tweet.author_id), 'conversation_id': tweet.conversation_id, 'created_at':tweet.created_at.strftime("%d/%m/%Y %H:%M %Z"), 'text': tweet.text})

        return str(results)
    except Exception as e:
        return "API Error: " + str(e)

def tweet(message):
    try:
        client = tweepy.Client(bearer_token=token)
        response = client.create_tweet(text=message)
        print(response)
        return response
    except Exception as e:
        return "API Error: " + str(e)
