import os
import subprocess
import argh
import json
import requests

def get_docker_host():
	docker_host = (os.environ['DOCKER_HOST']
		.split('tcp://')[1]
		.split(':')[0]
	)
	return docker_host

def get_docker_server_port():
	docker_server_port = (
		subprocess.check_output(['docker', 'port', 'iseifrainforest_server_1'])
			.split(':')[1][:-1]
	)
	return docker_server_port

@argh.arg('-p', '--password', default='plaintext123')
@argh.arg('-f', '--input_file', default='data/users.jl')
@argh.arg('-h', '--server_host', default=None)
@argh.arg('-r', '--server_port', default=None)
def main(**kwargs):
	if kwargs['server_host'] == None:
		kwargs['server_host'] = get_docker_host()

	if kwargs['server_port'] == None:
		kwargs['server_port'] = get_docker_server_port()

	for line in file(kwargs['input_file']).readlines():
		data = json.loads(line)

		url = ('http://'
			+kwargs['server_host']+':'
			+str(kwargs['server_port'])
			+'/api/users/'
			+str(data['cloud_id'])
			+'?pw='+kwargs['password']
		)
		# print url

		user_obj = {
		    'cloud_id' : data['cloud_id'],
		    'user_email' : data['user_email'], 
		    'user_pw' : data['user_pw'], 
		    'total_events_logged' : 0, 
		    'active' : True,
		    'first_timestamp' : None,
		    'last_timestamp' : None,
		}
		data_str = json.dumps(user_obj)

		print data['cloud_id'], requests.post(url, data_str)
		# print data['cloud_id'], requests.get(url).content

argh.dispatch_command(main)

