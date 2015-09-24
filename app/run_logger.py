"""
CLI tool to run the main get_new_rainforest_data method in EagleDataLogger.

Usage:
	python run_logger.py --help
"""

import argh
import redis

from logger import EagleDataLogger

redis_host = 'localhost'
redis_port = 6379
db = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

@argh.arg('-i', '--cloud_id', type=str, default="00000", help='')
@argh.arg('-t', '--last_timestamp', type=int, default=0, help='')
def main(**kwargs):
    EagleDataLogger.get_new_rainforest_data(
    	db,
    	{
	        'cloud_id' : kwargs['cloud_id'],
	        'last_timestamp' : kwargs['last_timestamp'],
	    })

argh.dispatch_command(main)








