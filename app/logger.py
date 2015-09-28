import requests
import json
import datetime
import time
import logging
from subprocess import Popen

import eagle_http

import util

class EagleDataLogger(object):

    @classmethod
    def get_new_rainforest_data(cls, redis_conn, config, filepath='../data/logs/', bucket_name='agong-iseif-temp',):
        #s3_rotation_log_filepath='../data/logs/', s3_rotation_log_level=logging.DEBUG,
        """
        Expected format for config:
        {
            cloud_id
            last_timestamp: (unix epoch) The timestamp of the last recorded event
        }

        Format for user_info (retrieved from redis with cloud_id as a key)
        {
            cloud_id
            user_email
            user_pw
            total_events_logged
            first_timestamp: (unix epoch) The timestamp of the first recorded event
            last_timestamp: (unix epoch) The timestamp of the last recorded event
        }

        """
        logging.info('get_new_rainforest_data')

        now = util.convert_datetime_to_unix_epoch(datetime.datetime.now())
        user_info = cls.fetch_user_info(redis_conn, config)
        log_filename = cls.get_log_filename(user_info, now)

        #Fetch data
        rainforest_data = cls.fetch_instantaneous_data(user_info)
        last_timestamp = cls.get_last_timestamp(rainforest_data)

        #Write data to disk
        util.build_dirs(filepath+log_filename)
        event_strings = [json.dumps(event)+"\n" for event in rainforest_data]
        #! This file should probably be managed as a member of
        #! a pool of connections that stays open for as long as needed
        file(filepath+log_filename, 'ab').write(''.join(event_strings))

        #Rotate logs to S3 if necessary
        if cls.is_new_log_filename(user_info, user_info['last_timestamp'], now):
            cls.rotate_log_to_s3(user_info, user_info['last_timestamp'], filepath, bucket_name)

        #Update user_info in redis
        user_info['last_timestamp'] = now
        if user_info['first_timestamp'] == None:
            user_info['first_timestamp'] = now
        user_info['total_events_logged'] = user_info['total_events_logged'] + len(rainforest_data)
        cls.update_user_info(redis_conn, user_info)


        return rainforest_data


    @classmethod
    def fetch_user_info(cls, redis_conn, config):
        """
        Fetch user_info from redis, using config.cloud_id as a key
        """
        user_str = redis_conn.get(config['cloud_id'])

        if user_str == None:
            raise ValueError('No user with cloud_id '+str(config['cloud_id'])+' exists.')

        logging.info("Fetching user info...")
        logging.debug("\tuser_str:"+user_str)
        user_obj = json.loads(user_str)

        return user_obj

    @classmethod
    def update_user_info(cls, redis_conn, user_info):
        """
        Fetch user_info from redis, using config.cloud_id as a key
        """
        redis_conn.set(user_info['cloud_id'], json.dumps(user_info))

    @classmethod
    def fetch_instantaneous_data(cls, user_info):
        """
        Fetch data from the Rainforest server and return it as a list of json_blobs
        """
        logging.info("Fetching instantaneous demand...")

        single_json_blob = eagle_http.get_instantaneous_demand(
            user_info['cloud_id'],
            user_info['user_email'],
            user_info['user_pw']
        )
        # print json.dumps(single_json_blob, indent=2)
        rainforest_data = [single_json_blob]

        return rainforest_data

    @classmethod
    def rotate_log_to_s3(cls, user_info, last_timestamp, filepath, bucket_name):
        """
        Kick off an asynchronous call to rotate a logfile to S3.
        """
        logging.info("Kicking off S3 log rotation...")

        raw_filename = filepath+EagleDataLogger.get_log_filename(user_info, last_timestamp)
        s3_bucket_name = bucket_name
        s3_filename = EagleDataLogger.get_s3_keyname(user_info, last_timestamp)

        log_filename = filepath+'rotate/rotate.log'
        logging.debug('\t'+raw_filename)
        logging.debug('\t'+s3_bucket_name)
        logging.debug('\t'+s3_filename)
        logging.debug('\t'+log_filename)

        Popen(['python', 'app/rotate_logs_to_s3.py',
            raw_filename, s3_bucket_name, s3_filename,
            '--log_file='+log_filename,
            '--log_level=20',
        ])

    # @classmethod
    # def push_next_request_to_queue(cls, config):
    #     print "Pushing next request to the queue"
    #     pass


    ### Time methods ###

    @classmethod
    def get_last_timestamp(cls, rainforest_data):
        """
        Get the most recent timestamp from a list of rainforest events.
        """

        max_timestamp = 0

        for event in rainforest_data:
            max_timestamp = max(max_timestamp, event['TimeStamp'])

        return max_timestamp

    @classmethod
    def is_new_log_filename(cls, user_info, last_timestamp, now):
        """
        Check whether the old log filename is the same as the new one.
        """

        #In case last_timestamp isn't defined yet:
        if last_timestamp == None:
            return False

        return cls.get_log_filename(user_info, last_timestamp) != cls.get_log_filename(user_info, now)

    ### File path methods ###

    @classmethod
    def get_log_filename(cls, user_info, now):
        """
        Get the filename and path for storing this logfile locally.
        """
        # print '-'*80
        # print user_info
        # print now
        now_dt = datetime.datetime.utcfromtimestamp(now)
        cloud_id_str = str(user_info['cloud_id'])
        return  now_dt.strftime("%Y-%m-%d-%H") +\
            "/iseif-rainforest-" + cloud_id_str + now_dt.strftime("-%Y-%m-%d-%H.jl")

    @classmethod
    def get_s3_keyname(cls, user_info, last_timestamp):
        """
        Get the keyname for storing this logfile on S3.
        """

        now_dt = datetime.datetime.utcfromtimestamp(last_timestamp)
        cloud_id_str = str(user_info['cloud_id'])
        return 'rainforest-logs/' + cloud_id_str + now_dt.strftime("/%Y/%m/%d") +\
            "/iseif-rainforest-" + cloud_id_str + now_dt.strftime("-%Y-%m-%d-%H.jl")


