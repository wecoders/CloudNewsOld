# -*- encoding: utf-8 -*-
#!/usr/bin/env python


def build_queue(qtype, **kwargs):
    if qtype == "redis":
        return build_redis_queue(**kwargs)
    else:
        return build_gevent_queue(**kwargs)

def build_gevent_queue(basesize=0):
    from gevent_queue import GeventQueue
    return GeventQueue(basesize)

def build_redis_queue(qname, host='localhost', port=6379, db=0):
    from gevent_queue import GeventQueue
    return GeventQueue(qname,host,port,db)

