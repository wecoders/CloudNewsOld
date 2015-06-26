# -*- encoding: utf-8 -*-
#!/usr/bin/env python

import time
import redis
import json

class RedisQueue(object):
    
    max_timeout = 0.3

    def __init__(self, qname="mq", host='localhost', port=6379, db=0):       
        self.qname = qname
        self.redis = redis.StrictRedis(host=host, port=port, db=db)
        
        
    def qsize(self):
        return self.redis.llen(self.qname) 

    def empty(self):
        if self.qsize() == 0:
            return True
        else:
            return False

    def put(self, obj):
        print("queue put",self.qname, json.dumps(obj))
        return self.redis.rpush(self.qname, json.dumps(obj))

    def put_first(self, obj):
        print("queue put first", self.qname, json.dumps(obj))
        return self.redis.lpush(self.qname, json.dumps(obj))

    def get(self):
        ret = self.redis.lpop(self.qname)
        if ret is None:
            return None
        print("queue get", self.qname, type(ret), ret)
        return json.loads(ret.decode(encoding='UTF-8'))

Queue = RedisQueue
