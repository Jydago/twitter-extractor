# Twitter Extractor
A small project to download tweets, process them and save in a database.
Can be used as a starting point for working with tweet data.


### Requirements
- Docker
- Docker-compose (should already be included when installing Docker on Windows or Mac)


### Project setup
- The project uses python as the main programming language.
- To simplify development without having to install any requirements except docker, 
all the code and database have been setup to run in docker containers.
- Jupyter notebooks are used as part of the development process.
- Pytest is used for testing.
  - Test files are found in `tests/`
- Postgres is used as the database.
  - Initial tables are set with `init-schema.sql`
- To interact with the Twitter API, [twarc](https://twarc-project.readthedocs.io/en/latest/) has been used.
- To configure the pipeline, create a `.env` file with the fields given in the `.env_example` file. 

#### Data pipeline
The data pipeline is made up of three steps, 
- **raw tweet download**
  - Found in `twitter_extractor/main_download_raw_tweets.py`
  - Downloads tweets using the recent tweets search api.
    - The query filters out retweets and only gets english tweets.
  - The specific search keywords, the number of api requests and number of tweets per request
  can be configured in the .env file. 
  - Downloaded tweets are saved in data/raw/ with [JSON Lines format](https://jsonlines.org/) and gzip compression. 
- **processing raw tweets**
  - Found in `twitter_extractor/main_process_tweets.py`
  - Extracts useful fields from tweets,
  organises them in a tabular format,
  does some basic data tests,
  and saves them in data/processed with [parquet file format](https://parquet.apache.org/).
  - Tweets that can't be processed or don't pass the data tests are saved separately to ease investigation.
  - The extracted data columns corresponds to the columns defined in the tweets table in `init-schema.sql`.
- **ingest processed tweets**
  - Found in `twitter_extractor/main_database_ingest_tweets.py`
  - Inserts processed tweets into the postgres database without regards for any existing data in the database, 
  i.e. there is currently no logic for upserts, so each ingestion adds more data, 
  regardless if the data is already there.

All the three steps have been combined and can be run from the root `main.py` file
to stitch them together into a pipeline.
Currently, the steps save files 
In a more realistic pipeline, each step would be in its own container 
and would therefore require some kind of orchestration to ensure that each step is run in the right order, 
time, and acting on the correct file.



### Instructions
- Ensure that you have a `.env` file in root with the correct configurations; see `.env_example` for template.
- After you've run a `docker-compose up` command,
you should run `docker-compose down` to take down all containers that have been started.
- Connection credentials to the database can be found in `compose.yaml`.


#### Development
To set up the development environment, 
including a jupyter notebook environment, 
run in a command line in the root folder
```
docker-compose build pipeline_development
docker-compose up pipeline_development
```
This will start two containers, one for the postgres database and one for jupyter notebook.
The jupyter notebook container has a volume attached to the root folder, 
so you can access all the code in python files from within jupyter.
To access the jupyter notebook instance,
copy the notebook token outputted in the command line 
and then navigate to [localhost:8881](http://localhost:8881) and input the copied token.


#### Testing
Tests can be found in the tests folder.
To run the tests,
run in a command line in the root folder
```
docker-compose build test
docker-compose up test
```
This will start one container that will run all the python tests.


#### Run pipeline
To run the pipeline,
run in a command line in the root folder
```
docker-compose build processing_pipeline
docker-compose up processing_pipeline
```
This will start two containers, one for the postgres database and one for running the python pipeline.
Once the second container is done, we can connect to the database and query the data.


### Potential improvements
- Implement `UPSERT` based on retrieved_date, search_keyword, and tweet_id instead of just `INSERT`.
  - Because given that we can find the same tweet (but potentially with new data)
  for each time we run the pipeline, 
  it would be good to not have duplicated data, but instead update the current field.
- Implement a pipeline where each step outputs the name of the files that it has saved. 
These should then be used as input for the next step. 
- Implement dynamic naming logic, e.g. add timestamp to file name, so we don't always overwrite data files.