import redis
import json

redis_host = 'localhost'
redis_port = 6379
db = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

keys = db.keys()
print "=== Keys: ==="
print keys

for key in keys:
	user_obj = json.loads(db.get(key))
	print key, '\t', json.dumps(user_obj, indent=2)
