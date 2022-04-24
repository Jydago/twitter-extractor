from pathlib import Path
for f in Path.cwd().iterdir():
    print(str(f))

from datetime import datetime

import pytest
from dateutil.tz import tzutc

from twitter_extractor.exceptions import FailedDataTestError
from twitter_extractor.main_process_tweets import process_tweet


def test_process_tweet():
    raw_tweet = {
        "public_metrics": {
            "retweet_count": 0,
            "reply_count": 1,
            "like_count": 2,
            "quote_count": 3
        },
        "created_at": "2020-01-02T03:04:05.000Z",
        "id": "2222",
        "text": "This is a tweet",
        "reply_settings": "everyone",
        "lang": "en",
        "author_id": "1111",
        "author": {
            "created_at": "2021-02-03T04:05:06.000Z",
            "public_metrics": {
                "followers_count": 4,
                "following_count": 5,
                "tweet_count": 6,
                "listed_count": 7
            },
            "id": "1111",
            "username": "tweet_user",
            "name": "tweet_name"
        },
        "__twarc": {
            "retrieved_at": "2022-03-04T05:06:07+00:00"
        },
        "meta_search_keywords": "tweet"
    }
    expected_tweet = {
        "tweet_id": "2222",
        "created_at": datetime(2020, 1, 2, 3, 4, 5, tzinfo=tzutc()),
        "text": "This is a tweet",
        "lang": "en",
        "reply_settings": "everyone",
        "tweet_type": "tweet",
        "like_count": 2,
        "reply_count": 1,
        "retweet_count": 0,
        "quote_count": 3,
        "mention_count": 0,
        "hashtags": "",
        "author_id": "1111",
        "author_followers_count": 4,
        "author_following_count": 5,
        "author_tweet_count": 6,
        "author_listed_count": 7,
        "author_created_at": datetime(2021, 2, 3, 4, 5, 6, tzinfo=tzutc()),
        "meta_search_keywords": "tweet",
        "meta_tweet_retrieved_at": datetime(2022, 3, 4, 5, 6, 7, tzinfo=tzutc())
    }
    assert process_tweet(raw_tweet) == expected_tweet


def test_process_tweet_negative_numbers():
    raw_tweet = {
        "public_metrics": {
            "retweet_count": -1,
            "reply_count": 1,
            "like_count": 2,
            "quote_count": 3
        },
        "created_at": "2020-01-02T03:04:05.000Z",
        "id": "2222",
        "text": "This is a tweet",
        "reply_settings": "everyone",
        "lang": "en",
        "author_id": "1111",
        "author": {
            "created_at": "2021-02-03T04:05:06.000Z",
            "public_metrics": {
                "followers_count": 4,
                "following_count": 5,
                "tweet_count": 6,
                "listed_count": 7
            },
            "id": "1111",
            "username": "tweet_user",
            "name": "tweet_name"
        },
        "__twarc": {
            "retrieved_at": "2022-03-04T05:06:07+00:00"
        },
        "meta_search_keywords": "tweet"
    }
    with pytest.raises(FailedDataTestError):
        process_tweet(raw_tweet)
