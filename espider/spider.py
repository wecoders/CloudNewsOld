# -*- coding: utf-8 -*-
#!/usr/bin/env python
import time

from .cron import every
from .utils import md5string

class EasySpider:
    def __init__(self, project_cfg):
        self.project = project_cfg.get('project', 'unknown')
        
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
        pass

    def _add_task(self, task_cfg):
        pass

    def fetch(self, url, **kwargs): #callback, url_type=None):
        task_id = md5string(url)
        task_cfg = {}

        if kwargs.get('callback'):
            callback = kwargs['callback']
            task_cfg['callback'] = getattr(callback, '__name__')
            if hasattr(callback, '_cfg'):
                cfg = callback._cfg
                if 'age' in cfg:
                    task_cfg['age'] = cfg['age']
                if 'priority' in cfg:
                    task_cfg['priority'] = cfg['priority']

        if kwargs.get('url_type'):
            task_cfg['url_type'] = kwargs['url_type']

        self._add_task(task_cfg)
        
    def _run_task(self, response, task_cfg):
        # task_id = md5string(task_cfg['url'])
        func = getattr(self, task_cfg.get('callback', '__call__'))
        # headers = task_cfg.get('headers', {})
        # response = self._fetch_url(url, headers)
        return self._run_callback(func, response, task_cfg)

    def _run_callback(self, func, *arguments):
        args, varargs, keywords, defaults = inspect.getargspec(function)
        return function(*arguments[:len(args) - 1])

    #def index_page(self, response):
        #self.fetch('some-url2', callback=self.detail_page)



