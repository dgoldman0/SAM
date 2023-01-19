# Eventually it would be helpful if SAM could start interacting with the broader outside world. One way is through Twitter integration.
from tweepy.asynchronous import AsyncClient
import os
import asyncio

bearer_token = os.environ['TWITTER_BEARER_TOKEN']
client = AsyncClient(bearer_token, wait_on_rate_limit = True)

id = "22993266"

async def main():
    next_token = None
    while True:
        print("Getting Tweets:")
        tweets = await client.get_users_mentions(id=id, tweet_fields=['context_annotations','created_at','geo', 'author_id'], max_results = 5, pagination_token = next_token)
        next_token = tweets.meta['next_token']
        for tweet in tweets.data:
            print(tweet)
            print()
        await asyncio.sleep(10)

asyncio.run(main())
