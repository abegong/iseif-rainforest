"""

#Get user with cloud_id 42013
curl localhost:8000/api/user/42013

#Post user with cloud_id 42013
curl localhost:8000/api/user/42013 -H "Content-Type: application/json" -X POST -d '{"type":"cat","object":{"species":"tiger"},"context":{}}'
"""


import json
import datetime
import redis

import tornado.ioloop
import tornado.web
from tornado.options import define, options

import util

tornado.options.define("port", default="8000")
tornado.options.define("redis_host", default="localhost")
tornado.options.define("redis_port", default="6379")
tornado.options.define("debug", default=True)

"""
#!!! All of these functions have been moved to utility scripts.
class UserHandler(tornado.web.RequestHandler):
    def get(self, cloud_id):
        user_obj = self.application.settings['redis'].get(cloud_id)
        if user_obj == None:
            raise tornado.web.HTTPError(400, reason='No user with cloud_id '+str(cloud_id)+' exists.')
        
        self.write({
            'status': 'success',
            'user' : user_obj,
        })

    def post(self, cloud_id):
        now_dt = datetime.datetime.now()
        now = util.convert_datetime_to_unix_epoch(now_dt)

        try:
            data = json.loads(self.request.body)
        except ValueError:
            raise tornado.web.HTTPError(400, reason="Request body must be a valid JSON object.")

        print data
        for key in ['user_email', 'user_pw']:
            if not key in data:
                raise tornado.web.HTTPError(400, reason="Event JSON must contain field "+key)

        #! Eventually, we may want to be smart about overwriting existing user records.
        #! For now, don't worry about it.
        # old_user_obj = self.application.settings['redis'].get(cloud_id)
        # if old_user_obj == None:
        #     pass
        # else:
        #     pass

        user_obj = {
            'cloud_id' : cloud_id, 
            'user_email' : data['user_email'], 
            'user_pw' : data['user_pw'], 
            'total_events_logged' : 0, 
            'active' : True,
            'first_timestamp' : now,
            'last_timestamp' : now,
        }
        self.application.settings['redis'].set(cloud_id, user_obj)

        self.write({
            'status': 'success',
            'user' : user_obj,
        })
"""

class EventHandler(tornado.web.RequestHandler):
    def post(self):

        self.write({
            'status': 'success',
            'user' : user_obj,
        })


application = tornado.web.Application([
        # (r"/", tornado.web.RedirectHandler, {'url': '/home'}),
        (r"/api/event/", EventHandler),
        # (r"/api/user/(.*?)", UserHandler),
    ],
    debug=options.debug,
    redis=redis.StrictRedis(host=options.redis_host, port=options.redis_port, db=0),
)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    application.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

