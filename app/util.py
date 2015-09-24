import datetime
import os

def build_dirs(filename):
    """
    Check to see whether the parent directories for the given filename exist.
    If they don't, then create them.

    !!! This function is a bit brittle: assumes a relative path starting with '../'
    """

    dir_list = filename.split('/')
    # print dir_list

    for i in range(1, len(dir_list)):
        temp_dir = '/'.join(dir_list[:i])
        # print temp_dir
        if not os.path.exists(temp_dir):
            # print 'trying...'
            os.makedirs(temp_dir)

#http://stackoverflow.com/questions/6999726/how-can-i-convert-a-datetime-object-to-milliseconds-since-epoch-unix-time-in-p
def convert_datetime_to_unix_epoch(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()
