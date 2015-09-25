"""
python -m unittest tests
"""

import unittest
import datetime

import util
from logger import EagleDataLogger
from pinger import SixSecondPinger

class TestLogger(unittest.TestCase):

    ### Test time methods ###

    def test_get_last_timestamp(self):
        self.assertEqual(
            EagleDataLogger.get_last_timestamp([
                {'TimeStamp': 20},
                {'TimeStamp': -20},
                {'TimeStamp': 105},
                {'TimeStamp': 120},
                {'TimeStamp': 200},
            ]),
            200
        )

        self.assertEqual(
            EagleDataLogger.get_last_timestamp([
                {'TimeStamp': 20},
            ]),
            20
        )

    ### Test filepath methods ###

    def test_is_new_log_filename(self):

        x = util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,1,0,0))

        self.assertEqual(
            EagleDataLogger.is_new_log_filename(
                {'cloud_id' : 99999},
                util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,1,0,0)),
                util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,1,0,0))
            ),
            False
        )

        self.assertEqual(
            EagleDataLogger.is_new_log_filename(
                {'cloud_id' : 99999},
                util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,1,0,0)),
                util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,1,0,30))
            ),
            False
        )

        self.assertEqual(
            EagleDataLogger.is_new_log_filename(
                {'cloud_id' : 99999},
                util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,1,0,0)),
                util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,1,0,59))
            ),
            False
        )

        self.assertEqual(
            EagleDataLogger.is_new_log_filename(
                {'cloud_id' : 99999},
                util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,1,0,0)),
                util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,1,1,0))
            ),
            True
        )

        self.assertEqual(
            EagleDataLogger.is_new_log_filename(
                {'cloud_id' : 99999},
                util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,1,0,59)),
                util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,1,1,0))
            ),
            True
        )

        self.assertEqual(
            EagleDataLogger.is_new_log_filename(
                {'cloud_id' : 99999},
                util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,1,1,0)),
                util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,2,3,4))
            ),
            True
        )

        #This case should never occur
        self.assertEqual(
            EagleDataLogger.is_new_log_filename(
                {'cloud_id' : 99999},
                util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,1,1,0)),
                util.convert_datetime_to_unix_epoch(datetime.datetime(2014,1,1,1,0))
            ),
            True
        )

    def test_get_log_filename(self):
        self.assertEqual(
            EagleDataLogger.get_log_filename(
                {'cloud_id' : 99999},
                util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,2,3,4)),
            ),
            '../data/logs/2015-01-02-03/iseif-rainforest-99999-2015-01-02-03.jl'
        )

    def test_get_s3_keyname(self):
        self.assertEqual(
            EagleDataLogger.get_s3_keyname(
                {'cloud_id' : 99999},
                util.convert_datetime_to_unix_epoch(datetime.datetime(2015,1,2,3,4)),
            ),
            'rainforest-logs/99999/2015/01/02/iseif-rainforest-99999-2015-01-02-03.jl'
        )


    #!!! These other functions all require API calls.
    #!!! Tricky (and less valuable) to bring under test.
    # def test_get_new_rainforest_data(self):
    # def test_fetch_user_info(self):
    # def test_fetch_data(self):
    # def test_rotate_log_to_s3(self):
    # def test_push_next_request_to_queue(self):

class TestPinger(unittest.TestCase):
    def test_get_wait_time(self):
        ssp = SixSecondPinger(None, None)

        self.assertEqual(
            ssp.get_wait_time(
                datetime.datetime.fromtimestamp(100),
                datetime.datetime.fromtimestamp(200),
            ),
            0
        )

        self.assertEqual(
            ssp.get_wait_time(
                datetime.datetime.fromtimestamp(100),
                datetime.datetime.fromtimestamp(101),
            ),
            5
        )

        self.assertEqual(
            ssp.get_wait_time(
                datetime.datetime.fromtimestamp(100),
                datetime.datetime.fromtimestamp(110),
            ),
            0
        )

        #This case shouldn't happen: most recent data is from the future...?
        self.assertEqual(
            ssp.get_wait_time(
                datetime.datetime.fromtimestamp(200),
                datetime.datetime.fromtimestamp(100),
            ),
            106
        )

        self.assertEqual(
            ssp.get_wait_time(
                datetime.datetime.fromtimestamp(100),
                datetime.datetime.fromtimestamp(100),
            ),
            6
        )



def main():
    unittest.main()

if __name__ == '__main__':
    main()