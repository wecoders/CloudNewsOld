# -*- encoding: utf-8 -*-
#!/usr/bin/env python

from gevent import queue


class GeventQueue(object):
    
    def __init__(self, qsize):
        self.q = queue.Queue(qsize)


    def qsize(self):
        return self.q.qsize()

    def empty(self):
        if self.qsize() == 0:
            return True
        else:
            return False

    def put(self, obj):
        self.q.put(obj)

    def get(self):
        return self.q.get()


Queue = GeventQueue
