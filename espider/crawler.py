# -*- coding: utf-8 -*-
#!/usr/bin/env python
import gevent
from gevent import monkey, queue

# monkey.patch_all()
import os
import json
import time
import logging
import traceback

from .utils import merge_cookie, import_object
from .mq import build_queue
from .fetcher import Fetcher
from .config import import_config
from .db import Session, ScopedSession, SpiderProject, SpiderTask, SpiderScheduler

class EasyCrawler:
    def __init__(self, timeout=5, workers_count=5, min_capacity=10, pipeline_size=100, loop_once=False):
        self.load_projects()
        self.load_spiders()
        self.timeout = timeout
        self.loop_once = loop_once
        self.qin = build_queue("redis")
        # self.qout = build_queue("redis") 
        self.jobs = [gevent.spawn(self.do_scheduler)]
        self.jobs += [gevent.spawn(self.do_task)]
        for project in self.projects:
            self.jobs += [gevent.spawn(self.do_worker, project.name, self.spiders.get(project.name))]
        # self.jobs += [gevent.spawn(self.do_worker) for i in range(workers_count)]
        # self.jobs += [gevent.spawn(self.do_pipeline)]
        self.job_count = len(self.jobs)
        # self.lock = threading.Lock()
        self.fetcher = Fetcher()
        self.db = ScopedSession()

    def load_projects(self):
        projects =  SpiderProject.load_projects() #query.filter_by(status=1).all()
        self.projects = []
        now = time.time()
        for project in projects:
            project.load_time = now
            self.projects.append(project)

    def load_spiders(self):
        self.spiders = {}
        self.taskqs = {}
        for project in self.projects:
            try:
                Spider = import_object("projects.%s.spider.Spider"% (project.name))
                config = import_config("projects/%s/project.yaml" % (project.name))
                spider = Spider()
                spider.config = config
                self.spiders[project.name] = spider
                self.taskqs[project.name] = build_queue("redis", qname="q_"+project.name)
            except Exception as e:
                raise e
        
        print("task qs:", self.taskqs)

    def start(self):
        gevent.joinall(self.jobs)

    def do_scheduler(self):
        now = time.time()
        schedulers = SpiderScheduler.query.filter(SpiderScheduler.next_time<=now).all()
        for s in schedulers:
            if s.process is None or s.process == "":
                process = {}
            else:
                process = json.loads(s.process)
            task = {}
            task['type'] = 'scheduler'
            task['id'] = s.id
            task['project'] = s.project
            task['task_id'] = s.task_id
            task['url'] = s.url
            if 'crontab' in process:
                crons = process.get('crontab')
                cronjob = CronJob(crons)
                task['next_time'] = cronjob.next(s.last_time)
            if 'callback' in process:
                task['callback'] = process.get('callback')
            inq = self.taskqs.get(s.project)
            inq.put(json.dumps(task))
        gevent.sleep(2)

    def do_task(self):
        try:
           
            while True:
                now = time.time()
                for project in self.projects:
                    if project.load_time > now:
                        continue
                    taskq = self.taskqs.get(project.name)
                    if taskq.qsize() <= 0:
                        new_tasks = self._load_tasks(project.name)
                        tasks_size = len(new_tasks)
                        if tasks_size <= 0:
                            logging.info('project [%s] load no task' % project.name)
                            project.load_time = now + 60*1000 
                            continue
                        else:
                            logging.info('project [%s] load %d tasks' % (project.name, tasks_size))
                        for t in new_tasks:
                            taskq.put(t)

                else:
                    gevent.sleep(2)
        except Exception as e:
            logging.error("Scheduler Error!\n%s" % traceback.format_exc())
        

    def do_worker(self, project_name, spider):

        try:
            # task = self.qin.get()
            taskq = self.taskqs.get(project_name)
            task_json = taskq.get()
            task = json.loads(task_json)
            while task != StopIteration:
                try:
                    if task is None:
                        gevent.sleep(2)
                        logging.info("worker [%s] get no task, sleep 2 seconds" % (project_name))
                        continue
                    # print("project %s task: " % project, task)
                    self.do_fetch(project_name, spider, task)
                except:
                    logging.error("Worker error!\n%s" % traceback.format_exc())

                
                task = taskq.get()
                
        finally:
            
            logging.debug("Worker done, ==========================  job count: %s" % self.job_count)

    
    def do_fetch(self, project_name, spider, task):
        print("task: ", task)
        if project_name != task['project']:
            pass
        headers = spider.config.headers
        url = task.get('url')
        if url.startswith('data://'):
            cb_name = task.get('callback')
            
            callback = getattr(spider, cb_name)
             
            print(spider, cb_name, callback)
            getattr(spider, cb_name)()
            if callback:
                callback()
        else:
            response = self.fetcher.fetch(spider, task, headers)
            if 'set-cookie' in response:
                new_cookie = response['set-cookie']
                old_cookie = headers.get('Cookie', None)
                headers['Cookie'] = merge_cookie(new_cookie, old_cookie)


    def _load_tasks(self, project_name):
        tasks = SpiderTask.query.filter(SpiderTask.project==project_name, SpiderTask.status==0).order_by('priority').limit(30).all()
        
        new_tasks = []
        for task in tasks:
            task.status = 1
            self.db.add(task)
            new_task={}
            new_task['id'] = task.id
            new_task['task_id'] = task.task_id
            new_task['project'] = task.project
            new_task['url'] = task.url
            new_task['process'] = task.process
            new_tasks.append(new_task)
        self.db.commit()

        return new_tasks


    # def do_pipeline(self):
    #     pipeline_size = 0
    #     while self.job_count > 1 or not self.qout.empty():
    #         sleep(self.timeout)
    #         logging.debug("pipeline sleep, job count: %d" % self.job_count)
    #         try:
    #             results = []
    #             try:
    #                 i=0
    #                 while i<2:
    #                     i+=1
    #                     pipeline_size += 1
    #                     results.append(self.qout.get_nowait())
                        
    #                 if len(results) > 0:
    #                     self.spider.pipeline(results)
    #             except queue.Empty:
    #                 if len(results) > 0:
    #                     self.spider.pipeline(results)
    #         except:
    #             logging.error("Pipeline error!\n%s" % traceback.format_exc()) 
        

