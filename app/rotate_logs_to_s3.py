"""
CLI tool to rotate log files to S3

Usage:
    python rotate_log_to_s3.py --help

    python app/rotate_logs_to_s3.py data/temp agong-iseif-temp temp-00001.gz


NB: This script uses its own S3 connection for uploading.
It would be more efficient to use a single connection and upload all the files in a directory at once.

"""

import argh
import gzip
import shutil
import os
import logging

import boto
from boto.s3.key import Key

@argh.arg('raw_filename')
@argh.arg('s3_bucket_name')
@argh.arg('s3_filename')
@argh.arg('-z', '--no_zip', default=False)
@argh.arg('-r', '--no_remove', default=False)
@argh.arg('-d', '--dry_run', default=False)
@argh.arg('-v', '--verbose', default=True)
@argh.arg('-l', '--log_level', default=logging.DEBUG)
@argh.arg('-f', '--log_file', default='rotate.log')
def main(raw_filename, s3_bucket_name, s3_filename, **kwargs):
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        filename=kwargs['log_file'],
        level=kwargs['log_level'],
    )
    try:

        logging.info('='*80)
        logging.info('Hello, rotate!')
        logging.debug('\tdry_run='+str(kwargs['dry_run']))

        if kwargs['dry_run']:
            kwargs['verbose'] = True

        zipped_filename = raw_filename+'.gz'

        if kwargs['verbose']:
            logging.info('Generating zipped file '+ zipped_filename)

        if not kwargs['dry_run']:
            #Zip the file
            with open(raw_filename, 'rb') as f_in, gzip.open(zipped_filename, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)


        #Connect to S3
        if kwargs['verbose']:
            logging.info('Connecting to S3')

        if not kwargs['dry_run']:
            #! This requires AWS credentials to be defined in .bashrc, etc.
            s3_conn = boto.connect_s3()

        if kwargs['verbose']:
            logging.info('Getting bucket '+ s3_bucket_name)

        if not kwargs['dry_run']:
            #! Maybe we should make sure the bucket exists/create it if it doesn't?
            # s3_conn.get_all_buckets()
            # s3_conn.create_bucket('agong-iseif-temp')

            bucket = s3_conn.get_bucket(s3_bucket_name)


        if kwargs['verbose']:
            logging.info('Uploading zipped file to '+ s3_filename)

        if not kwargs['dry_run']:
            #Upload the zipped file
            k = Key(bucket)
            k.key = s3_filename

            #! Maybe we should check to see if the key exists already?

            k.set_contents_from_filename(zipped_filename)#, cb=percent_cb, num_cb=10)

        #Delete the file and zipped file
        if kwargs['verbose']:
            logging.info('Deleting zipped and original files')

        if not kwargs['dry_run']:
            os.remove(raw_filename)
            os.remove(zipped_filename)

    except (SystemExit, KeyboardInterrupt):
        raise

    except Exception, e:
        logging.error('Fatal error :', exc_info=True)


argh.dispatch_command(main)
