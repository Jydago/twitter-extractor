import os

import polars as pl
import psycopg2
from dotenv import load_dotenv
from loguru import logger
from psycopg2 import extras
from psycopg2 import sql

from twitter_extractor import utils


def load_processed_tweets() -> pl.DataFrame:
    processed_data_folder = utils.get_data_folder() / "processed"
    processed_data_file = processed_data_folder / "processed_twitter_data.parquet"
    df = pl.read_parquet(processed_data_file)
    return df


def create_insert_statement(data_columns: list[str]) -> sql.Composed:
    # create sql identifiers for the column names
    # we do this to safely insert this into a sql query
    sql_columns = sql.SQL(", ").join(sql.Identifier(name) for name in data_columns)

    # create placeholders for the values.
    values = sql.SQL(", ").join([sql.Placeholder() for _ in data_columns])

    schema_name = "twitter"
    table_name = "tweets"

    insert_statement = sql.SQL("INSERT INTO {} ({}) VALUES({});").format(
        sql.Identifier(schema_name, table_name), sql_columns, values
    )
    return insert_statement


def save_in_database(conn, df: pl.DataFrame, insert_statement: sql.Composed):
    # Convert polars Date type to python datetime for psycopg2 to be able to handle dates
    for col in df:
        if col.dtype == pl.Date:
            df = df.with_column(col.dt.to_python_datetime())
    cur = conn.cursor()
    extras.execute_batch(cur, insert_statement, df.rows())
    conn.commit()


def main():
    logger.info("Started database_ingest_tweets")

    conn = psycopg2.connect(
        host=os.environ["DATABASE_HOST"],
        user=os.environ["DATABASE_USER"],
        password=os.environ["DATABASE_PASSWORD"],
        dbname=os.environ["DATABASE_DB_NAME"]
    )
    logger.info("Loading processed tweets")
    df = load_processed_tweets()
    logger.info("Creating insert statement")
    insert_statement = create_insert_statement(df.columns)
    logger.info("Saving tweets to database")
    save_in_database(conn, df, insert_statement)
    logger.info("Finished database_ingest_tweets")


if __name__ == '__main__':
    load_dotenv()
    main()
