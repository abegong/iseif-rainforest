
## Architecture

1. Tasks are submitted to an AWS SNS queue.
2. They're received by a tornado server, which
	1. Fetches events from Rainforest
	2. Stores them locally to logfiles, broken out by user cloud_id
	3. Rotates logs to S3 every hour


#### Redis
The tornado server caches data locally in redis.
This gives us a convenient way to store state. (We're not really using this right now.)
More importantly, it lets us store user names and PWs in a more secure way. (They don't have to be encoded with every SQS task.)


So the moving parts are:
* SNS
* Tornado server
* Rainforest server
* Redis
* Local logfiles
* S3


## EagleDataLogger
logger.EagleDataLogger contains most of the core business logic.
This class can be called from tests, a simple CLI (run_logger.py), or from the tornado webserver.




## Status

What's working as of 9/12/2015:

The core methods for the logger class are in pretty good shape:

	def get_wait_time(cls, last_timestamp, now):
	def get_last_timestamp(cls, rainforest_data):
	def is_new_log_filename(cls, user_info, last_timestamp, now):
	def get_log_filename(cls, user_info, now):
	def get_s3_keyname(cls, user_info, last_timestamp):

They're under test, and the master method is built:

	def get_new_rainforest_data(cls, redis_conn, config):

The four methods that make API calls are scaffolded, but not built yet:

	def fetch_user_info(cls, redis_conn, config):
	def fetch_data(cls, user_info, last_timestamp):
	def rotate_log_to_s3(cls, user_info, last_timestamp):
	def push_next_request_to_queue(cls, config):

## More stuff that's done:

	Bring up Redis
	Implement fetch_user_info
	Wrap the whole thing in a tornado server
	Add a tornado method to populate redis

	Create a fake user data set

	Suppress wait_time
	Get run_logger working with redis
	Suppress push_next_request_to_queue


## Next steps:

	Develop triggering script
	Migrate wait_time to separate triggering script

	Dockerize it
	Add configs for redis, SNS, rainforest, S3, etc.

	Write a fake fetch_data method
	Write a *real* fetch_data method

	Develop the rotate_log_to_s3 method

	Develop the push_next_request_to_queue method

	Test the whole cycle
	Add some cleaner documentation

	Write a monitoring script to track 
	Come up with a future-proof plan for sharding






But I think it’s a better use of our time to nail down Anthem