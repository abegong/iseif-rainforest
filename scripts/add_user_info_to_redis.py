import redis
import json

input_file = 'data/users.jl'

redis_host = 'localhost'
redis_port = 6379
db = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

# db.flushdb()

for line in file(input_file).readlines():
	data = json.loads(line)

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

	db.set(data['cloud_id'], data_str)
