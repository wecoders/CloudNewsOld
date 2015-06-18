# -*- coding: utf-8 -*-
#!/usr/bin/env python
import gevent
from gevent import monkey, queue

# monkey.patch_all()
import json

from .utils import merge_cookie
from .mq import build_queue
from .fetcher import Fetcher
from .config import import_config
from .db import SpiderProject, SpiderTask, SpiderScheduler

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
            self.jobs += [gevent.spawn(self.do_worker, project, self.spiders.get(project))]
        # self.jobs += [gevent.spawn(self.do_worker) for i in range(workers_count)]
        # self.jobs += [gevent.spawn(self.do_pipeline)]
        self.job_count = len(self.jobs)
        # self.lock = threading.Lock()
        self.fetcher = Fetcher()

    def load_projects(self):
        self.projects =  SpiderProject.load_projects() #query.filter_by(status=1).all()


    def load_spiders(self):
        self.spiders = {}
        self.taskqs = {}
        for project in self.projects:
            try:
                spider = import_object("projects.%s.spider.Spider"% (project.name))
                config = import_config("projects.%s.project.yaml" % (project.name))
                spider.config = config
                self.spiders[project.name] = spider
                self.taskqs[project.name] = build_queue("redis", "task_"+project.name)
            except Exception as e:
                raise e
            

    def start(self):
        gevent.joinall(self.jobs)

    def do_scheduler(self):
        now = time.time()
        schedulers = SpiderScheduler.query.filter(SpiderScheduler.next_time<=now).all()
        for s in schedulers:
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
                task['next_time'] = cronjob.next(now)
            if 'callback' in process:
                task['callback'] = process.get('callback')

            self.qin.put(task)
        gevent.sleep(2)

    def do_task(self):
        try:
           
            while True:
                for project in self.projects:
                    taskq = self.taskqs.get(project)
                    if taskq.qsize() <= 0:
                        new_tasks = self._load_tasks(project)
                        for t in new_tasks:
                            taskq.put(t)

                else:
                    gevent.sleep(2)
        except Exception as e:
            logging.error("Scheduler Error!\n%s" % traceback.format_exc())
        

    def do_worker(self, project, spider):

        try:
            # task = self.qin.get()
            taskq = self.taskqs.get(project)
            task = taskq.get()
            while task != StopIteration:
                try:
                    self.do_fetch(project, spider, task)
                except:
                    logging.error("Worker error!\n%s" % traceback.format_exc())

                
                task = taskq.get()
                
        finally:
            
            logging.debug("Worker done, ==========================  job count: %s" % self.job_count)

    
    def do_fetch(self, project, spider, task):
        if project != task['project']:
            pass
        headers = spider.headers
        response = self.fetcher.fetch(spider, task, headers)
        if 'set-cookie' in response:
            new_cookie = response['set-cookie']
            old_cookie = headers.get('Cookie', None)
            headers['Cookie'] = merge_cookie(new_cookie, old_cookie)


    def _load_tasks(self, project):
        tasks = SchedulerTask.query.filter(SchedulerTask.project==project, SchedulerTask.status==0).order_by('priority').limit(30).all()
        db = session()
        new_tasks = []
        for task in tasks:
            task.status = 1
            db.add(task)
            new_task={}
            new_task['id'] = task.id
            new_task['task_id'] = task.task_id
            new_task['project'] = task.project
            new_task['url'] = task.url
            new_task['process'] = task.process
            new_tasks.append(new_task)
        db.commit()
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
        

