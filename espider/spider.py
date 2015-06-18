# -*- coding: utf-8 -*-
#!/usr/bin/env python
import time

from .cron import every
from .utils import md5str

from espider.db.model import SpiderScheduler
from espider.db import Session

class EasySpider:
    def __init__(self):
        self.project = 'unknown'
        self.headers = {}
        self._tasks = {}
        
        # self.site_id = site.settings.site_id
        self.headers = site.settings.headers
        self.settings = site.settings
        
        if self.settings.page.parser:
            self.page_rules = self.settings.page.rules
            for page_rule in self.page_rules:
                #print type(page_rule), page_rule
                rule = page_rule.rule.strip()
                r = re.compile(rule)
                page_rule.re = r
        else:
            self.page_rules = []


        self.target_rules = self.settings.target.rules
        for target_rule in self.target_rules:
            rule = target_rule.rule.strip()
            #print rule
            r = re.compile(rule)
            target_rule.re = r

        self.target_parser = self.settings.target.parser
        self.page_parser = self.settings.page.parser
               
 
        if self.settings.debug is None or not self.settings.debug:
            self.debug = False
        else:
            self.debug = True


        if self.settings.sleep_second:
            self.sleep_second = float(self.settings.sleep_second)
        else:
            self.sleep_second = 0

    def _on_start(self):
        if hasattr(self, 'on_start'):
            func = getattr(self, 'on_start')
            is_crontab = False
            if hasattr(func, '_is_crontab'):
                is_crontab = getattr(func, '_is_crontab')
                if is_crontab:
                    crons = getattr(func, '_crons')
                    self.crons = crons
            scheduler_cfg = {}
            scheduler_cfg['func'] = 'on_start'
            scheduler_cfg['project'] = self.project
            scheduler_cfg['spider'] = self.__name__
            kwargs = {}
            if is_crontab:
                scheduler_cfg['crontab'] = self.crons
            scheduler_cfg['next_time'] = int(time.time())
            return scheduler_cfg
        else:
            raise NotImplementedError("project %s() function 'on_start' not implemented!" % self.project)



    # @every(cron=[])
    # def on_start(self):
        #self.fetch('some-url', url_type='index', callback=self.index_page)
        # pass

    def _add_scheduler(self, scheduler_cfg):
        project = scheduler_cfg['project']
        task_id = 'data://%s/%s' % (scheduler_cfg['project'], scheduler_cfg['func'])
        url = 'data://%s' % (scheduler_cfg['func'])
        crontab = json.dumps(scheduler_cfg.get('crontab', []))
        next_time = int(time.time())
        
        scheduler = SpiderScheduler()
        scheduler.project = project
        scheduler.task_id = task_id
        scheduler.url = url
        scheduler.process = json.dumps({'callback':scheduler_cfg['func'], 'crontab':crontab})
        scheduler.next_time = next_time
        scheduler.last_time = next_time
        session.add(scheduler)
        session.commit()


    def _add_task(self, task_cfg):
        project = task_cfg['project']
        task_id = task_cfg['task_id']
        url = task_cfg['url']
        crontab = json.dumps(scheduler_cfg.get('crontab', '[]'))
        last_time = int(time.time())
        age = int(task_cfg.get('age', 10*365*24*60*60)) #10years
        next_time = last_time+int(age)
        priority = task_cfg.get('priority', 0)
        callback = task_cfg.get('callback', None)

        task = SpiderTask()
        task.project = project
        task.task_id = task_id
        task.url = url
        task.callback = callback
        task.next_time = last_time
        task.last_time = last_time
        task.priority = priority
        task.process = json.dumps({'callback':scheduler_cfg['func']})
        session.add(task)
        session.commit()


        pass

    def fetch(self, url, callback=None, **kwargs)::
        task_id = md5str(url)
        task_cfg = {}
        task_cfg['task_id'] = task_id

        if callback is not None:
            task_cfg['callback'] = getattr(callback, '__name__')
            if hasattr(callback, '_cfg'):
                cfg = callback._cfg
                if 'age' in cfg:
                    task_cfg['age'] = cfg['age']
                if 'priority' in cfg:
                    task_cfg['priority'] = cfg['priority']

        self._add_task(task_cfg)
        
    def _run_task(self, response, task_cfg):
        func = getattr(self, task_cfg.get('callback', '__call__'))
        return self._run_callback(func, response, task_cfg)

    def _run_callback(self, func, *arguments):
        args, varargs, keywords, defaults = inspect.getargspec(function)
        return function(*arguments[:len(args) - 1])




