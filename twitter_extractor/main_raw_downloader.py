import gzip
import os
import functools

import ujson
from dotenv import load_dotenv
from twarc.client2 import Twarc2
from twarc.expansions import ensure_flattened

import utils


def without_field(d: dict, field: str):
    d.pop(field)
    return d


def get_tweets(t: Twarc2) -> list[dict]:
    query = f'{os.environ["TWEET_SEARCH_KEYWORD"]} -is:retweet lang:en'
    expansions = ("author_id,referenced_tweets.id,in_reply_to_user_id,"
                  "entities.mentions.username,referenced_tweets.id.author_id")
    tweet_fields = ("id,created_at,text,author_id,in_reply_to_user_id,"
                    "referenced_tweets,entities,public_metrics,lang,reply_settings")
    user_fields = "id,created_at,name,username,public_metrics"

    max_results = int(os.environ["TWEETS_PER_REQUEST"])
    search_results = t.search_recent(
        query=query,
        expansions=expansions,
        tweet_fields=tweet_fields,
        user_fields=user_fields,
        max_results=max_results
    )

    tweets = []
    max_tweet_pages = int(os.environ["TWEETS_PAGES"])
    for i, page in enumerate(search_results, 1):
        tweets.extend([without_field(tweet, "__twarc") for tweet in ensure_flattened(page)])

        if i == max_tweet_pages:
            break

    return tweets


def save_tweets(tweets: list[dict]):
    raw_data_folder = utils.get_data_folder() / "raw"
    raw_data_folder.mkdir(parents=True, exist_ok=True)

    raw_data_file = raw_data_folder / "raw_twitter_data.jl"
    json_dumper = functools.partial(ujson.dumps, ensure_ascii=False, escape_forward_slashes=False)
    if int(os.environ["COMPRESSED_RAW_DATA"]):
        with gzip.open(raw_data_file.with_suffix(".jl.gzip"), "wt") as f:
            for tweet in tweets:
                f.write(json_dumper(tweet) + "\n")
    else:
        with raw_data_file.open("w") as f:
            for tweet in tweets:
                f.write(json_dumper(tweet) + "\n")


def main():
    t = Twarc2(bearer_token=os.environ["BEARER_TOKEN"])
    tweets = get_tweets(t)
    save_tweets(tweets)


if __name__ == "__main__":
    load_dotenv()
    main()
