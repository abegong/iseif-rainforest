import datetime
import os

def build_dirs(filename):
    """
    Check to see whether the parent directories for the given filename exist.
    If they don't, then create them.

    NB: For directories, this function assumes a trailing slash

    Examples to turn into unit tests later.
    [util.build_dirs(x) for x in ['../data/logs/', '../data/logs', 'data/logs', 'data/logs/', '/data/logs/', '/data/logs/filename']]
    --------------------------------------------------------------------------------
    * ../data/logs/
    ../data
    ../data/logs
    --------------------------------------------------------------------------------
    * ../data/logs
    ../data
    --------------------------------------------------------------------------------
    * data/logs
    data
    --------------------------------------------------------------------------------
    * data/logs/
    data
    data/logs
    --------------------------------------------------------------------------------
    * /data/logs/
    /data
    /data/logs
    --------------------------------------------------------------------------------
    * /data/logs/filename
    /data
    /data/logs

    """

    dir_list = filename.split('/')
    # print '-'*80
    # print '*', filename

    for i in range(0, len(dir_list)-1):
        temp_dir = '/'.join(dir_list[:i+1])
        if dir_list[i] not in ['', '..']:
            # print temp_dir
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
                pass

#http://stackoverflow.com/questions/6999726/how-can-i-convert-a-datetime-object-to-milliseconds-since-epoch-unix-time-in-p
def convert_datetime_to_unix_epoch(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()
