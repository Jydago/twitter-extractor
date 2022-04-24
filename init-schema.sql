-- noinspection SqlNoDataSourceInspectionForFile

create schema twitter
--  Use text instead of varchar, seems like the performance hit is negligible
--  See: https://stackoverflow.com/questions/4848964/difference-between-text-and-varchar-character-varying
--  Anyways easier to handle length limitations if needed in code
    create table tweets
    (
        tweet_id text not null,
        created_at timestamp not null,
        text text not null,
        lang text not null,
        reply_settings text not null,
        tweet_type text not null,
        like_count integer not null,
        reply_count integer not null,
        retweet_count integer not null,
        quote_count integer not null,
        mention_count integer not null,
        hashtags text not null,  -- comma separated list
        author_id text not null,
        author_followers_count integer not null,
        author_following_count integer not null,
        author_tweet_count integer not null,
        author_listed_count integer not null,
        author_created_at timestamp not null,
        meta_search_keywords text not null,
        meta_tweet_retrieved_at timestamp not null
    )
