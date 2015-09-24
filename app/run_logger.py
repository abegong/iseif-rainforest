"""
CLI tool to run the main get_new_rainforest_data method in EagleDataLogger.

Usage:
	python run_logger.py --help
"""

import argh
from logger import EagleDataLogger

@argh.arg('-i', '--cloud_id', type=int, default=100000, help='')
@argh.arg('-t', '--last_timestamp', type=int, default=0, help='')
def main(**kwargs):
    EagleDataLogger.get_new_rainforest_data(
    	"REDIS CONNECTION SHOULD GO HERE. INSTEAD WE PASS A STUPID STRING",
    	{
        'cloud_id' : kwargs['cloud_id'],
        'last_timestamp' : kwargs['last_timestamp'],
    })

argh.dispatch_command(main)








