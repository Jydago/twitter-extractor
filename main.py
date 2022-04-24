from dotenv import load_dotenv
from loguru import logger

from twitter_extractor import main_download_raw_tweets, main_process_tweets, main_database_ingest_tweets

if __name__ == '__main__':
    logger.info("Started pipeline")
    load_dotenv()

    main_download_raw_tweets.main()
    main_process_tweets.main()
    main_database_ingest_tweets.main()

    logger.info("Finished pipeline")
