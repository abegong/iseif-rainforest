"""
CLI tool to rotate log files to S3

Usage:
    python rotate_log_to_s3.py --help

    python app/rotate_logs_to_s3.py data/temp agong-iseif-temp temp-00001.gz

"""

import argh
import gzip
import shutil
import os

import boto
from boto.s3.key import Key

@argh.arg('raw_filename')
@argh.arg('s3_bucket_name')
@argh.arg('s3_filename')
@argh.arg('-z', '--no_zip', default=False)
@argh.arg('-r', '--no_remove', default=False)
@argh.arg('-d', '--dry_run', default=False)
@argh.arg('-v', '--verbose', default=True)
def main(raw_filename, s3_bucket_name, s3_filename, **kwargs):
    if kwargs['dry_run']:
        kwargs['verbose'] = True

    # filenames = get_filenames(user_info, last_timestamp)
    zipped_filename = raw_filename+'.gz'

    if kwargs['verbose']:
        print 'Generating zipped file', zipped_filename

    if not kwargs['dry_run']:
        #Zip the file
        with open(raw_filename, 'rb') as f_in, gzip.open(zipped_filename, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


    #Connect to S3
    if kwargs['verbose']:
        print 'Connecting to S3'

    if not kwargs['dry_run']:
        #! This requires AWS credentials to be defined in .bashrc, etc.
        s3_conn = boto.connect_s3()

    if kwargs['verbose']:
        print 'Getting bucket', s3_bucket_name

    if not kwargs['dry_run']:
        #! Maybe we should make sure the bucket exists/create it if it doesn't?
        # s3_conn.get_all_buckets()
        # s3_conn.create_bucket('agong-iseif-temp')

        bucket = s3_conn.get_bucket(s3_bucket_name)


    if kwargs['verbose']:
        print 'Uploading zipped file to', s3_filename

    if not kwargs['dry_run']:
        #Upload the zipped file
        k = Key(bucket)
        k.key = s3_filename

        #! Maybe we should check to see if the key exists already?

        k.set_contents_from_filename(zipped_filename)#, cb=percent_cb, num_cb=10)

    #Delete the file and zipped file
    if kwargs['verbose']:
        print 'Deleting zipped and original files'

    if not kwargs['dry_run']:
        os.remove(raw_filename)
        os.remove(zipped_filename)



argh.dispatch_command(main)
