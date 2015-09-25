"""

Usage:
	python pinger.py --help
"""

import argh
import redis

import requests
import json
import datetime

def fetch_cloud_id_list():
	redis_host = 'localhost'
	redis_port = 6379
	db = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

	cloud_id_list = db.keys()
	return cloud_id_list

def ping_cloud_id(cloud_id, url='localhost', port=8000):
	rval = requests.get('http://'+url+':'+str(port)+'/api/event/'+str(cloud_id))
	print rval.text

def ping_all_cloud_ids(cloud_id_list):
	for cloud_id in cloud_id_list:
		ping_cloud_id(cloud_id)

def main(**kwargs):
	cloud_id_list = fetch_cloud_id_list()
	while 1:
		print '-'*80
		print datetime.datetime.now()
		ping_all_cloud_ids(cloud_id_list)
		# print datetime.datetime.now()

argh.dispatch_command(main)








