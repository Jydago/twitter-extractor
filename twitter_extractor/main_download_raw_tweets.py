import functools
import gzip
import os

import ujson
from dotenv import load_dotenv
from loguru import logger
from twarc.client2 import Twarc2
from twarc.expansions import ensure_flattened

from twitter_extractor import utils


def get_tweets(t: Twarc2, tweet_search_keyword: str, tweets_per_request: int, max_tweet_requests: int) -> list[dict]:
    query = f'{tweet_search_keyword} -is:retweet lang:en'
    expansions = ("author_id,referenced_tweets.id,in_reply_to_user_id,"
                  "entities.mentions.username,referenced_tweets.id.author_id")
    tweet_fields = ("id,created_at,text,author_id,in_reply_to_user_id,"
                    "referenced_tweets,entities,public_metrics,lang,reply_settings")
    user_fields = "id,created_at,name,username,public_metrics"

    search_results = t.search_recent(
        query=query,
        expansions=expansions,
        tweet_fields=tweet_fields,
        user_fields=user_fields,
        max_results=tweets_per_request
    )

    tweets = []
    for i, tweets_request in enumerate(search_results, 1):
        for tweet in ensure_flattened(tweets_request):
            tweet["meta_search_keywords"] = tweet_search_keyword
            tweets.append(tweet)

        if i == max_tweet_requests:
            break

    return tweets


def save_raw_tweets_local(tweets: list[dict]):
    raw_data_folder = utils.get_data_folder() / "raw"
    raw_data_folder.mkdir(parents=True, exist_ok=True)

    raw_data_file = raw_data_folder / "raw_twitter_data.jsonl.gzip"
    json_dumper = functools.partial(ujson.dumps, ensure_ascii=False, escape_forward_slashes=False)
    with gzip.open(raw_data_file, "wt") as f:
        for tweet in tweets:
            f.write(json_dumper(tweet) + "\n")


def main():
    logger.info("Started raw_download_tweets")
    twitter_bearer_token = os.environ["BEARER_TOKEN"]
    tweet_search_keyword = os.environ["TWEET_SEARCH_KEYWORD"]
    tweets_per_request = int(os.environ["TWEETS_PER_REQUEST"])
    max_tweet_requests = int(os.environ["TWEETS_PAGES"])

    t = Twarc2(bearer_token=twitter_bearer_token)
    logger.info("Downloading raw tweets")
    tweets = get_tweets(t, tweet_search_keyword, tweets_per_request, max_tweet_requests)
    logger.info("Saving raw tweets")
    save_raw_tweets_local(tweets)

    logger.info("Finished raw_download_tweets")


if __name__ == "__main__":
    load_dotenv()
    main()
