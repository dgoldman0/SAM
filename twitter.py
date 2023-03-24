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
        return str(results) + "\nNext Token(can be used to get the next block of results): " + str(tweets.meta.get("next_token"))
    except Exception as e:
        return "API Error: " + str(e) + " | An error like this one can be caused by a number of issues, including an incorrect user id. Also note that @ should not be used in the query string."

# Get user info by ID (starts with #) or username (starts with @)
def userInfo(ident):
    id = None
    username = None
    if ident.startswith("#"):
        id = ident[1:]
    elif ident.startswith("@"):
        username = ident[1:]
    else:
        return "Invalid format for identity. Use # to find user by ID and @ to find user by username."
    global token
    try:
        client = tweepy.Client(bearer_token=token)
        user = client.get_user(id = id, username = username, user_fields = ['id', 'name', 'username', 'created_at', 'location', 'url', 'description', 'verified_type']).data
        return str({'id': user.id, 'name': user.name, 'username': user.username, 'created_at': user.created_at, 'location': user.location, 'url': user.url, 'bio': user.description, 'verified_type': user.verified_type})
    except Exception as e:
        return "API Error: " + str(e)

# Get user info by ID (starts with #) or username (starts with @)
def userFollowers(ident, next_token = None):
    global token
    try:
        client = tweepy.Client(bearer_token=token)
        followers = client.get_users_followers(id = ident, next_token = next_token, user_fields = ['description'], max_results = 25)
        follower_data = []
        data = followers.data
        for follower in data:
            follower_data.append({'id': follower.id, 'username': follower.username, 'bio': follower.description})
        return str(follower_data) + "\nNext Token(can be used to get the next block of results): " + str(followers.meta.get("next_token"))
    except Exception as e:
        return "API Error: " + str(e)

# Get user info by ID (starts with #) or username (starts with @)
def userFollowing(ident, next_token = None):
    global token
    try:
        client = tweepy.Client(bearer_token=token)
        followers = client.get_users_following(id = ident, next_token = next_token, user_fields = ['description'], max_results = 25)
        follower_data = []
        data = followers.data
        for follower in data:
            follower_data.append({'id': follower.id, 'username': follower.username, 'bio': follower.description})
        return str(follower_data) + "\nNext Token(can be used to get the next block of results): " + str(followers.meta.get("next_token"))
    except Exception as e:
        return "API Error: " + str(e)

def tweet(message):
    # Need to get these still
    global client_id
    global client_secret
    try:
        auth = tweepy.OAuthHandler(client_id, client_secret)
        auth.set_access_token(os.environ.get("twitter_access_token"), os.environ.get("twitter_access_token_secret"))
        api = tweepy.API(auth)
        api.update_status(message)
        return "Tweeted: " + message
    except Exception as e:
        return "API Error: " + str(e)

def tweetWithMedia(message, media):
    # Need to get these still
    global client_id
    global client_secret
    try:
        auth = tweepy.OAuthHandler(client_id, client_secret)
        auth.set_access_token(os.environ.get("twitter_access_token"), os.environ.get("twitter_access_token_secret"))
        api = tweepy.API(auth)
        api.update_with_media(media, message)
        return "Tweeted: " + message
    except Exception as e:
        return "API Error: " + str(e)

def retweet(id):
    # Need to get these still
    global client_id
    global client_secret
    try:
        auth = tweepy.OAuthHandler(client_id, client_secret)
        auth.set_access_token(os.environ.get("twitter_access_token"), os.environ.get("twitter_access_token_secret"))
        api = tweepy.API(auth)
        api.retweet(id)
        return "Retweeted: " + id
    except Exception as e:
        return "API Error: " + str(e)

def reply(message, id):
    # Need to get these still
    global client_id
    global client_secret
    try:
        auth = tweepy.OAuthHandler(client_id, client_secret)
        auth.set_access_token(os.environ.get("twitter_access_token"), os.environ.get("twitter_access_token_secret"))
        api = tweepy.API(auth)
        api.update_status(message, in_reply_to_status_id=id)
        return "Replied to " + id + " with: " + message
    except Exception as e:
        return "API Error: " + str(e)

def like(id):
    # Need to get these still
    global client_id
    global client_secret
    try:
        auth = tweepy.OAuthHandler(client_id, client_secret)
        auth.set_access_token(os.environ.get("twitter_access_token"), os.environ.get("twitter_access_token_secret"))
        api = tweepy.API(auth)
        api.create_favorite(id)
        return "Liked: " + id
    except Exception as e:
        return "API Error: " + str(e)

def unlike(id):
    # Need to get these still
    global client_id
    global client_secret
    try:
        auth = tweepy.OAuthHandler(client_id, client_secret)
        auth.set_access_token(os.environ.get("twitter_access_token"), os.environ.get("twitter_access_token_secret"))
        api = tweepy.API(auth)
        api.destroy_favorite(id)
        return "Unliked: " + id
    except Exception as e:
        return "API Error: " + str(e)

if __name__ == '__main__':
    pass
