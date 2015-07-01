# -*- coding: utf-8 -*-
#!/usr/bin/env python
import time
import json
import logging
import inspect

from .cron import every
from .utils import md5str

from .db.model import SpiderScheduler, SpiderTask
from .db import ScopedSession

INIT=0
RUNNING=1
OK=200
SERVER_ERROR=500
SEVEN_DAYS=7*24*60*60

def add_metaclass(metaclass):
    """Class decorator for creating a class with a metaclass."""
    def wrapper(cls):
        orig_vars = cls.__dict__.copy()
        slots = orig_vars.get('__slots__')
        if slots is not None:
            if isinstance(slots, str):
                slots = [slots]
            for slots_var in slots:
                orig_vars.pop(slots_var)
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)
        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper


class BaseSpiderMeta(type):

    def __new__(cls, name, bases, attrs):
        print("meta attrs", attrs)
        newcls = type.__new__(cls, name, bases, attrs)
        newcls._cronjobs = []

        for each in attrs.values():
            if inspect.isfunction(each) and getattr(each, '_is_cronjob', False):
                newcls._cronjobs.append(each)
                print("cronjob", each)
        # newcls._min_tick = min_tick
        print("cronjobs", newcls._cronjobs)
        return newcls


@add_metaclass(BaseSpiderMeta)
class EasySpider(object):
    def __init__(self):
        self.project = 'unknown'
        self.config = {}
        self._tasks = {}
        # self._cronjobs = []
        
        # self.site_id = site.settings.site_id
        # XWA`

    def _on_start(self):
        # print("_on_start cronjob", self._cronjobs)
        tasks = []
        for job in self._cronjobs:
            crons  = getattr(job, '_crons', [])
            is_cronjob = getattr(job, '_is_cronjob', False)
            project = self.config.get('project')
            callback = job.__name__
            # print("_on_start cronjob", job, crons)
            url = u'data://%s/%s' % (self.config.get('project'), callback)
            task_id = md5str(url.encode('utf-8'))

            scheduler_cfg = {}
            scheduler_cfg['url'] = url
            scheduler_cfg['task_id'] = task_id
            scheduler_cfg['callback'] = callback 
            scheduler_cfg['project'] = project
            scheduler_cfg['crontab'] = crons
            logging.debug("project %s add scheduler, %s" % (project, json.dumps(scheduler_cfg)))
            self._add_scheduler(scheduler_cfg)
            task_cfg = {}
            task_cfg['project'] = project
            task_cfg['url'] = url
            task_cfg['task_id'] = task_id
            task_cfg['process'] = {'callback':callback}
            age = getattr(job, '_age', 0)
            priority = getattr(job, '_priority', 0)
            task_cfg['age'] = age
            task_cfg['priority'] = priority
            tasks.append(task_cfg)
        if len(tasks)>0:
            return None
        else:
            return None


        # if hasattr(self, 'on_start'):
        #     func = getattr(self, 'on_start')
        #     print("_on_start", self, func)
        #     is_crontab = False
        #     is_crontab = getattr(func, '_is_crontab')
        #     print("get is_crontab", is_crontab)
        #     if hasattr(func, '_is_crontab'):
        #         is_crontab = getattr(func, '_is_crontab')
        #         print("get is_crontab", is_crontab)
        #         if is_crontab:
        #             crons = getattr(func, '_crons')
        #             self.crons = crons
        #     scheduler_cfg = {}
        #     scheduler_cfg['callback'] = 'on_start'
        #     scheduler_cfg['project'] = self.config.get('project')
        #     # scheduler_cfg['spider'] = self.__name__
        #     kwargs = {}
        #     if is_crontab:
        #         scheduler_cfg['crontab'] = self.crons
        #     scheduler_cfg['next_time'] = int(time.time())
            
        #     self._add_scheduler(scheduler_cfg)
        # else:
        #     raise NotImplementedError("project %s() function 'on_start' not implemented!" % self.project)




    def _add_scheduler(self, scheduler_cfg):
        project = scheduler_cfg['project']
        crontab = scheduler_cfg.get('crontab', [])
        callback = scheduler_cfg.get('callback', '')
        url = u'data://%s/%s' % (scheduler_cfg['project'], callback)
        # print(url, type(url))
        task_id = md5str(url.encode('utf-8'))
        next_time = int(time.time())
        
        old_scheduler = SpiderScheduler.query.filter_by(task_id=task_id).first()
        if old_scheduler is not None:
            process = json.dumps({'callback':callback, 'crontab':crontab})
            old_scheduler.process = process
            old_scheduler.next_time = next_time
            db = ScopedSession()
            db.add(old_scheduler)
            db.commit() 
            return
        
        
        scheduler = SpiderScheduler()
        scheduler.project = project
        scheduler.task_id = task_id
        scheduler.url = url
        scheduler.process = json.dumps({'callback':scheduler_cfg['callback'], 'crontab':crontab})
        scheduler.next_time = next_time
        scheduler.last_time = next_time
        db = ScopedSession()
        db.add(scheduler)
        db.commit() 


    def _add_task(self, task_cfg):
        project = task_cfg['project']
        task_id = task_cfg['task_id']
        url = task_cfg['url']
        # crontab = json.dumps(task_cfg.get('crontab', '[]'))
        now = int(time.time())
        age = int(task_cfg.get('age', SEVEN_DAYS)) #10years
        next_time = now+int(age)
        priority = task_cfg.get('priority', 0)
        callback = task_cfg.get('callback', None)
        logging.info("project %s add task, %s" % (project, json.dumps(task_cfg)))
        oldtask = SpiderTask.query.filter_by(task_id=task_id).first()
        if oldtask is not None:
            if oldtask.status == 0:
                return
            # process = json.loads(oldtask.process)
            # age = process.get('age', SEVEN_DAYS)
            if now > oldtask.last_time+int(age) and oldtask.status != 1:
                oldtask.status = 0
                oldtask.process = json.dumps({'callback':callback})
                db = ScopedSession()
                db.add(oldtask)
                db.commit()
                return
            logging.info("project %s task %s exist" % (project, task_id))
            return
        task = SpiderTask()
        task.project = project
        task.task_id = task_id
        task.url = url
        # task.callback = callback
        #task.next_time = last_time
        task.last_time = now
        task.priority = priority
        task.status = 0
        task.result = None
        task.age = age
        task.callback = callback #process = json.dumps({'callback':callback}) #, 'age': task_cfg.get('age', 7*24*60*60)})
        db = ScopedSession()
        db.add(task)
        db.commit()
        # db.close()



    def fetch(self, url, callback=None, **kwargs):
        task_id = md5str(url)
        task_cfg = {}
        task_cfg['task_id'] = task_id
        task_cfg['project'] = self.config.project
        task_cfg['url'] = url
        if callback is not None:
            task_cfg['callback'] = getattr(callback, '__name__')
            if hasattr(callback, '_age'):
                task_cfg['age'] = callback._age
            if hasattr(callback, '_priority'):
                task_cfg['priority'] = callback._priority

        self._add_task(task_cfg)
        
    def _run_task(self, response, task_cfg):
        func = getattr(self, task_cfg.get('callback', '__call__'))
        return self._run_callback(func, response, task_cfg)

    def _run_callback(self, func, *arguments):
        args, varargs, keywords, defaults = inspect.getargspec(function)
        return function(*arguments[:len(args) - 1])




