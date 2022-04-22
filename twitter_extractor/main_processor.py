from dotenv import load_dotenv
import utils
import os
import json_lines
import polars as pl
import dateutil.parser


def process_tweet(raw_tweet: dict):
    d = dict()
    d["tweet_id"] = raw_tweet["id"]
    d["created_at"] = dateutil.parser.isoparse(raw_tweet["created_at"])
    d["text"] = raw_tweet["text"]
    d["lang"] = raw_tweet["lang"]
    d["reply_settings"] = raw_tweet["reply_settings"]

    public_metrics = raw_tweet["public_metrics"]
    d["like_count"] = public_metrics["like_count"]
    d["reply_count"] = public_metrics["reply_count"]
    d["retweet_count"] = public_metrics["reply_count"]
    d["quote_count"] = public_metrics["quote_count"]

    author_metric = raw_tweet["author"]["public_metrics"]
    d["author_id"] = raw_tweet["author"]["id"]
    d["author_created_at"] = dateutil.parser.isoparse(raw_tweet["author"]["created_at"])
    d["author_followers_count"] = author_metric["followers_count"]
    d["author_following_count"] = author_metric["following_count"]
    d["tweet_count"] = author_metric["tweet_count"]
    d["author_listed_count"] = author_metric["listed_count"]

    if "referenced_tweets" in raw_tweet:
        d["tweet_type"] = raw_tweet["referenced_tweets"][0]["type"]
    else:
        d["tweet_type"] = "tweet"

    d["mention_count"] = 0
    d["hashtags"] = ""
    if "entities" in raw_tweet:
        tweet_entities = raw_tweet["entities"]
        if "mentions" in tweet_entities:
            d["mention_count"] = len(tweet_entities["mentions"])

        if "hashtags" in tweet_entities:
            d["hashtags"] = ",".join([tag["tag"] for tag in tweet_entities["hashtags"]])

    return d


def main():
    raw_data_folder = utils.get_data_folder() / "raw"
    file_name = "raw_twitter_data.jl" + (".gzip" if int(os.environ["COMPRESSED_RAW_DATA"]) else "")
    raw_data_file = raw_data_folder / file_name

    all_data = []
    with json_lines.open(raw_data_file) as f:
        for i, raw_tweet in enumerate(f, 1):
            all_data.append(process_tweet(raw_tweet))

    df = pl.DataFrame(all_data)
    processed_data_folder = utils.get_data_folder() / "processed"
    processed_data_folder.mkdir(parents=True, exist_ok=True)
    processed_data_file = processed_data_folder / "processed_twitter_data.parquet"
    # Can't save as csv because of twitter text including \n
    df.write_parquet(processed_data_file)


if __name__ == "__main__":
    load_dotenv()
    main()
