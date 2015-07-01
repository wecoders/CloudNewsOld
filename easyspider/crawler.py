# -*- coding: utf-8 -*-
#!/usr/bin/env python
import gevent
from gevent import monkey, queue
from gevent.pool import Pool
from greenlet import GreenletExit
# monkey.patch_all()
import os
import json
import time
import logging
import traceback
import datetime

from .utils import merge_cookie, import_object
from .mq import build_queue
from .fetcher import Fetcher
from .config import import_config, Config
from .db import Session, ScopedSession, SpiderProject, SpiderTask, SpiderScheduler,SpiderResult
from .cron import CronJob

OK=True
START=1
STOP=-1

class EasyCrawler:
    def __init__(self, timeout=5, workers_count=1, min_capacity=10, pipeline_size=100, loop_once=False):
        
        self.spiders = {}
        self.queues = {}
        self.projects = {}
        self.jobs = {}

        self.pool = Pool(1000)
        
        self.timeout = timeout
        self.loop_once = loop_once
        self.qin = build_queue("redis", qname="command_q")
        # self.qout = build_queue("redis") 
        self.jobs['scheduler'] = self.pool.spawn(self.do_scheduler)
        self.jobs['command'] = self.pool.spawn(self.do_command)
        self.jobs['loader'] = self.pool.spawn(self.do_loader)
        self.jobs['tasks'] = {}
        self.jobs['common_tasks'] = []
        
        self.load_spiders()
        print("projects:",self.projects)
        self.queues['common'] = build_queue("redis", qname="common_q")
        for i in range(workers_count):
            project = Config()
            project.name = 'common'
            project.queue_name = 'common'
            job = self.pool.spawn(self.do_worker, project)
            self.jobs['common_tasks'] += [job]
        # for project in self.projects:
        #     self.jobs += [gevent.spawn(self.do_worker, project.name, self.spiders.get(project.name))]
        # self.jobs += [gevent.spawn(self.do_worker) for i in range(workers_count)]
        # self.jobs += [gevent.spawn(self.do_pipeline)]
        # self.job_count = len(self.jobs)
        # self.lock = threading.Lock()
        self.fetcher = Fetcher()
        self.db = ScopedSession()

    def load_spiders(self):
        projects =  SpiderProject.load_projects() #query.filter_by(status=1).all()
        
        for project in projects:
            self._load_project(project.name)
            
        
        print("task qs:", self.queues)

    def shutdown(self):
        self.pool.kill()

    def start(self):
        self.pool.join()
        # gevent.joinall(jobs)

    def do_command(self):
        while True:
            command = self.qin.get()
            if command is None:
                gevent.sleep(5)
                continue
            if 'op' in command:

                op = command.get('op')
                if op == 'exit':
                    self.pool.kill()
                else:
                    target = command.get('target')  #project, task
                    
                    if target == 'project':
                        if op == 'start':
                            target_id = command.get('target_id')
                            if target_id not in self.projects:
                                self._load_project(target_id)
                        if op == 'stop':
                            target_id = command.get('target_id')
                            if target_id  in self.projects:
                                self._unload_project(target_id)

    def _load_project(self, project):
        try:
            dbproject = SpiderProject.query.filter_by(name=project).first()
            if dbproject is None:
                logging.error("project %s not exits, can't loading." % project)
                return
            newproject = Config()
            newproject.name = project
            newproject.load_time = time.time()
            if dbproject.queue_name == 'common' or dbproject.queue_name is None:
                newproject.queue_name = 'common'
            else:
                newproject.queue_name = dbproject.queue_name

            Spider = import_object("projects.%s.spider.Spider"% (project))
            config = import_config("projects/%s/project.yaml" % (project))
            spider = Spider()
            spider.config = config
            spider.status = START
            new_tasks=spider._on_start()
            self.spiders[project] = spider
            self.projects[project] = newproject
            if newproject.queue_name != 'common':
                self.queues[project] = build_queue("redis", qname="q_"+project)
                job = self.pool.spawn(self.do_worker, newproject)
                self.jobs['tasks'][project] = job
                self.pool.start(job)
            if new_tasks is not None:
                queue = self.queues.get(newproject.queue_name)
                for task in new_tasks:
                    queue.put_first(task)
        except Exception as e:
            logging.error("load spider!\n%s" % traceback.format_exc())
            raise e

    def _unload_project(self, project):
        spider = self.spiders.get(project)
        spider.status = STOP
        job = self.jobs['tasks'].get(project)
        if job is not None:
            self.pool.killone(job)
            del self.jobs['tasks'][project]
        if project in self.queues:
            del self.queues[project]
        del self.spiders[project]
        del self.projects[project]

    def do_scheduler(self):
        while True:
            now = datetime.datetime.now()
            nowts = time.time()
            schedulers = SpiderScheduler.query.filter(SpiderScheduler.next_time<=nowts).all()
            logging.debug("load schedulers length is %d, time:%d" % (len(schedulers), nowts))
            for s in schedulers:
                if s.project not in self.projects:
                    logging.debug("project [%s] doesn't started." % (s.project))
                    continue

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
                    next_time = cronjob.next(now)
                    print("do scheduler", crons, now, nowts,next_time)
                    s.next_time = next_time
                    s.last_time = nowts
                    self.db.add(s)

                if 'callback' in process:
                    task['callback'] = process.get('callback')
                
                project = self.projects.get(s.project)
                if project is not None:
                    inq = self.queues.get(project.queue_name)
                    inq.put(task)
            self.db.commit()
            gevent.sleep(10)

    def do_loader(self):
        try:
           
            while True:
                now = time.time()
                for k,project in self.projects.items():
                    if project.load_time > now:
                        continue
                    spider = self.spiders.get(project.name)
                    if spider is None or spider.status != START:
                        logging.warn("spider (%s) is not ready." % project.name)
                        continue
                    taskq = self.queues.get(project.queue_name)
                    if taskq.qsize() <= 0:
                        new_tasks = self._load_tasks(project.name)
                        tasks_size = len(new_tasks)
                        if tasks_size <= 0:
                            logging.info('project [%s] load no task' % project.name)
                            #project.load_time = now + 10*1000 
                            continue
                        else:
                            logging.info('project [%s] load %d tasks' % (project.name, tasks_size))
                        for task in new_tasks:
                            # print("put in queue", json.dumps(task))
                            taskq.put(task)

                else:
                    gevent.sleep(2)
        except Exception as e:
            logging.error("Scheduler Error!\n%s" % traceback.format_exc())
        

    def do_worker(self, project):

        try:
            # task = self.qin.get()
            taskq = self.queues.get(project.queue_name)
            
            while True:

                try:
                    task = taskq.get()
                    if task == StopIteration or task == '':
                        ogging.info("worker [%s] get none task, exit do worker" % (project.name))
                        break
                    if task is None:
                        gevent.sleep(2)
                        logging.info("worker [%s] get no task, sleep 2 seconds" % (project.name))
                        continue

                    print("do worker get a task", task) 
                    project_name = task.get('project')
                    if project_name is None:
                        logging.error("worker get a task from queue [%s] has no project, ignore. %s" % (project.queue_name, json.dumps(task)))
                        continue
                    spider = self.spiders.get(project_name)
                    if spider is None:
                        logging.error("worker [%s] get no task, no spider, continue" % (project_name))
                        continue
                    # print("project %s task: " % project, task)
                    self.do_fetch(project_name, spider, task)
                except GreenletExit as ge:
                    # logging.info("Worker %s ")
                    pass
                except:
                    logging.error("Worker error!\n%s" % traceback.format_exc())

        
                
        finally:
            
            logging.debug("Worker done, ==========================  job count: %s" % project_name)

    
    def do_fetch(self, project, spider, task):
        print("do fetch task: ", task)
        if project != task['project']:
            pass
        headers = spider.config.headers
        url = task.get('url')
        task_id = task.get('task_id')
        if url.startswith('data://'):
            callback = task.get('callback')
            if callback is not None:
                callback_func = getattr(spider, callback)
                if callback_func:
                    callback_func()
        else:
            response = self.fetcher.fetch(spider, task, headers)
            if 'set-cookie' in response:
                new_cookie = response['set-cookie']
                old_cookie = headers.get('Cookie', None)
                headers['Cookie'] = merge_cookie(new_cookie, old_cookie)

            result_code = response['code']
            if 'result' in response:
                res = response['result']
                if 'code' in res:
                    result_code = res['code']
                sr = SpiderResult.query.filter_by(task_id=task_id).first()
                if sr is None:
                    sr = SpiderResult()
                sr.project = task.get('project')
                sr.task_id = task_id
                sr.url = url
                sr.content = json.dumps(res)
                sr.create_at = datetime.datetime.now()
                self.db.add(sr)
            st = SpiderTask.query.filter_by(task_id=task_id).first()
            st.status = result_code
            st.last_time = time.time()
            self.db.add(st)
            self.db.commit()
            # if 'process' in task:
            #     cb_name = task.get('process').get('callback')
            #     callback = getattr(spider, cb_name)
            #     if callback:
            #         callback(response)


    def _load_tasks(self, project):
        tasks = SpiderTask.query.filter(SpiderTask.project==project, SpiderTask.status==0).order_by('priority').limit(30).all()
        
        new_tasks = []
        for task in tasks:
            task.status = 1
            self.db.add(task)
            new_task={}
            new_task['id'] = task.id
            new_task['task_id'] = task.task_id
            new_task['project'] = task.project
            new_task['url'] = task.url
            new_task['callback'] = task.callback
            # if task.process is None or task.process == "":
            #     new_task['process'] = {}
            # else:
            #     new_task['process'] = json.loads(task.process)
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
        

