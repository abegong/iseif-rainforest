"""

Usage:
    python pinger.py --help
"""

import argh
import redis
import requests
import logging

import json
import datetime
import time
from collections import defaultdict

import util

class SixSecondPinger(object):

    max_wait = 6.0

    def __init__(self, api_url, redis_conn):
        self.api_url = api_url

        if redis_conn:
            self.redis_conn = redis_conn
            self.fetch_cloud_id_list()
        else:
            logging.warn('Warning: You really should declare redis_conn')

    def get_wait_time(self, last_timestamp, now):
        """
        Calculuate how long to wait, given the difference between the last_timestamp and now.
        If the difference is already greater than cls.max_wait, return 0.
        """

        diff = (now - last_timestamp).total_seconds()
        if diff < self.max_wait:
            return self.max_wait - diff
        else:
            return 0

    def fetch_cloud_id_list(self):
        logging.info('Fetching cloud_id_list...')
        self.cloud_id_list = self.redis_conn.keys()
        logging.debug('\tcloud_id_list: '+','.join(self.cloud_id_list))
        # print self.cloud_id_list

    def ping_cloud_id(self, cloud_id):
        # print self.api_url
        # print cloud_id
        response = requests.get(self.api_url+str(cloud_id))
        return response.status_code

    def ping_all_cloud_ids(self):
        result_dict = defaultdict(int)

        for cloud_id in self.cloud_id_list:
            result_dict[self.ping_cloud_id(cloud_id)] += 1

        return result_dict

    def ping_forever(self, verbose=False):
        count = 0
        while 1:
            # print self.cloud_id_list
            start_time = datetime.datetime.now()
            results = self.ping_all_cloud_ids()
            spare_time = self.get_wait_time(start_time, datetime.datetime.now())

            if verbose:
                logging.info(json.dumps({
                    'start_time' : util.convert_datetime_to_unix_epoch(start_time),
                    'results' : results,
                    'spare_time' : spare_time,
                }))

            #Fetch new cloud_id_list from redis every once in a while
            count += 1
            if count >= 10:
                self.fetch_cloud_id_list()
                count = 0

            time.sleep(spare_time)

@argh.arg('--app_host', type=str, default="localhost")
@argh.arg('--app_port', type=int, default=8000)
@argh.arg('--redis_host', type=str, default="localhost")
@argh.arg('--redis_port', type=int, default=6379)
@argh.arg('-v', '--verbose', default=False)
@argh.arg('-l', '--log_level', default=logging.DEBUG)
@argh.arg('-f', '--log_file', default='pinger.log')
def main(**kwargs):
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        filename=kwargs['log_file'],
        level=kwargs['log_level'],
    )
    logging.info('='*80)
    logging.info('Hello, pinger!')

    logging.info('Connecting to redis...')
    redis_conn = redis.StrictRedis(
        host=kwargs['redis_host'],
        port=kwargs['redis_port'],
        db=0
    )

    api_url = 'http://'+kwargs['app_host']+':'+str(kwargs['app_port'])+'/api/event/'
    logging.info('api_url: '+api_url)

    logging.info('Instantiating SixSecondPinger...')
    ssp = SixSecondPinger(
        api_url,
        redis_conn,
    )

    logging.info('Launching ping_forever...')
    ssp.ping_forever(verbose=kwargs['verbose'])

if __name__ == "__main__":
    argh.dispatch_command(main)








