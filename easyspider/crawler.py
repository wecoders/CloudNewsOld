# -*- coding: utf-8 -*-
#!/usr/bin/env python
import gevent
from gevent import monkey, queue
from gevent.pool import Pool
from greenlet import GreenletExit

import os
import imp
import json
import time
import logging
import traceback
import datetime

from .utils import merge_cookie, load_module
from .mq import build_queue
from .fetcher import Fetcher
from .config import import_config, Config
from .db import Session, ScopedSession, SpiderProject, SpiderTask, SpiderScheduler,SpiderResult
from .cron import CronJob
from .processor import EasyProcessor

OK=True
START=1
STOP=-1

class EasyCrawler:
    def __init__(self, timeout=5, workers_count=1, min_capacity=10, pipeline_size=100, loop_once=False):
        self.db = ScopedSession()
        # print(self.db)
        self.spiders = {}
        self.queues = {}
        self.processors = {}
        self.projects = {}
        self.jobs = {}

        self.pool = Pool(1000)
        
        self.timeout = timeout
        self.loop_once = loop_once
        self.qin = build_queue("redis", qname="command_q")
        # self.qout = build_queue("redis") 
        
        self.jobs['processors'] = {}
        self.jobs['common_tasks'] = []
        
        self.load_spiders()
        # print("projects:",self.projects)
        
        # self.jobs['loader'] = self.pool.spawn(self.do_loader)

        # self.queues['common'] = build_queue("redis", qname="common_q")
        # for i in range(workers_count):
        #     project = Config()
        #     project.name = 'common'
        #     project.queue_name = 'common'
        #     job = self.pool.spawn(self.do_worker, project)
        #     self.jobs['common_tasks'] += [job]
        # for project in self.projects:
        #     self.jobs += [gevent.spawn(self.do_worker, project.name, self.spiders.get(project.name))]
        # self.jobs += [gevent.spawn(self.do_worker) for i in range(workers_count)]
        # self.jobs += [gevent.spawn(self.do_pipeline)]
        # self.job_count = len(self.jobs)
        # self.lock = threading.Lock()
        self.fetcher = Fetcher()
        

    def load_spiders(self):
        projects =  SpiderProject.load_projects() #query.filter_by(status=1).all()
        names = []
        for project in projects:
            names.append(project.name)

        for project_name in names:
            self._load_project(project_name)
            
        
        # logging.debug("task queues:", self.queues)

    def shutdown(self):
        self.pool.kill()

    def start(self):
        
        self.jobs['scheduler'] = self.pool.spawn(self.do_scheduler)
        self.jobs['command'] = self.pool.spawn(self.do_command)
        self.pool.join()
        # self.pool.start(self.jobs['scheduler'])
        # self.pool.start(self.jobs['command'])
        
        # gevent.joinall(jobs)

    def do_command(self):
        while True:
            command = self.qin.get()
            logging.debug("get a command %s" % json.dumps(command))
            if command is None:
                gevent.sleep(5)
                continue
            if 'op' in command:

                op = command.get('op')
                if op == 'exit':
                    self.pool.kill()
                else:
                    target_type = command.get('type')  #project, task
                    target = command.get('target')
                    logging.debug("get a %s command: %s/%s" % (op, target_type, target))
                    if target_type == 'project':
                        if op == 'start':
                            self._load_project(target)
                        if op == 'stop':
                            if target == 'all':
                                for prj in self.projects:
                                    self._unload_project(prj)
                            else:
                                self._unload_project(target)
                        if op == 'reload':
                            self._unload_project(target)
                            job = self._load_project(target)
                            if job is not None:
                                self.pool.start(job)



    # def _load_module(self, filepath):

    #     class_name = None
    #     expected_class = 'Spider'

    #     mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])

    #     if file_ext.lower() == '.py':
    #         py_mod = imp.load_source(mod_name, filepath)
            
    #     if hasattr(py_mod, expected_class):
    #         class_name = getattr(py_mod, expected_class)

    #     return class_name

    # def _load_project(self, project):
    #     logging.debug("load project %s" % project)
    #     if project in self.projects:
    #         return
    #     try:
    #         dbproject = SpiderProject.query.filter_by(name=project).first()
    #         if dbproject is None:
    #             logging.error("project %s not exits, can't loading." % project)
    #             return
    #         newproject = Config()
    #         newproject.name = project
    #         newproject.load_time = time.time()
    #         if dbproject.queue_name == 'common' or dbproject.queue_name is None:
    #             newproject.queue_name = 'common'
    #         else:
    #             newproject.queue_name = dbproject.queue_name

    #         spider_cls = self._load_module("projects/%s/spider.py" % project)# import_object("projects.%s.spider.Spider"% (project))
    #         if spider_cls is None:
    #             logging.error("import module %s error.!" % project)
    #             return
    #         logging.debug("import spider %s" % project)
    #         config = import_config("projects/%s/project.yaml" % (project))
    #         spider = spider_cls()
    #         spider.config = config
    #         spider.status = START
    #         new_tasks=spider._on_start()
    #         self.spiders[project] = spider
    #         self.projects[project] = newproject
    #         if newproject.queue_name != 'common':
    #             self.queues[project] = build_queue("redis", qname="q_"+project)
    #             job = self.pool.spawn(self.do_worker, newproject)
    #             self.jobs['tasks'][project] = job
    #             self.pool.start(job)
    #         if new_tasks is not None:
    #             queue = self.queues.get(newproject.queue_name)
    #             for task in new_tasks:
    #                 queue.put_first(task)
    #     except Exception as e:
    #         logging.error("load spider!\n%s" % traceback.format_exc())
    #         raise e

    def _load_project(self, project):
        logging.debug("load project %s" % project)
        if project in self.projects:
            return
        return self._load_processor(project)


    def _load_processor(self, project):
        logging.debug("load processor %s" % project)
        try:
            dbproject = SpiderProject.query.filter_by(name=project).first()
            if dbproject is None:
                logging.error("project %s not exits, can't loading." % project)
                return
            newproject = Config()
            newproject.name = project
            newproject.load_time = time.time()
            if dbproject.queue_name is None:
                newproject.queue_name = dbproject.name
            else:
                newproject.queue_name = dbproject.queue_name

            spider_cls = load_module("projects/%s/spider.py" % project)# import_object("projects.%s.spider.Spider"% (project))
            if spider_cls is None:
                logging.error("import module %s error.!" % project)
                return
            logging.debug("import spider %s" % project)
            config = import_config("projects/%s/project.yaml" % (project))
            spider = spider_cls()
            spider.config = config
            spider.status = START
            
            self.spiders[project] = spider
            self.projects[project] = newproject
            queue_name = 'q_'+project #+"_"+str(int(time.time()))
            spider._on_start()
            # if new_tasks is not None:
            #     queue = build_queue('redis', queue_name)# self.queues.get(newproject.queue_name)
            #     for task in new_tasks:
            #         queue.put_first(task)
            #     queue.close()

            if newproject.queue_name != 'common':
                
                self.queues[project] = queue_name #build_queue("redis", qname="q_"+project)
                processor = EasyProcessor(project, spider, queue_name)
                job = self.pool.spawn(processor.run)
                self.jobs['processors'][project] = job
                # self.pool.start(job)
                self.processors[project] = processor
                return job

            
        except Exception as e:
            logging.error("load spider!\n%s" % traceback.format_exc())
            raise e
        return

    def _unload_project(self, project):
        logging.debug("unload project %s" % (project))
        old_project = self.projects.get(project)
        if old_project is None:
            return

        
        if old_project.queue_name != 'common':
            qname = self.processors.get(project)
            if qname is not None:
                # inq = build_queue('redis', qname=qname)
                # inq.put_first('')
                processor = self.processors[project]
                processor.status = 0
                del self.processors[project]
                del self.queues[project]

            # job = self.jobs['tasks'].get(project)
            # if job is not None:
                # self.pool.killone(job, block=False)
                # del self.jobs['tasks'][project]
            # if project in self.queues:
                # del self.queues[project]
        # spider = self.spiders.get(project)
        # spider.status = STOP
        del self.spiders[project]
        del self.projects[project]

    def do_scheduler(self):
        logging.debug("scheduler thread start")
        while True:
            now = datetime.datetime.now()
            nowts = time.time()
            new_projects = []
            schedulers = self.db.query(SpiderScheduler).filter(SpiderScheduler.next_time<=nowts).all()
            logging.debug("load schedulers length is %d" % (len(schedulers)))
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
                    # print("do scheduler", crons, now, nowts,next_time)
                    s.next_time = next_time
                    s.last_time = nowts
                    self.db.add(s)

                if 'callback' in process:
                    task['callback'] = process.get('callback')
                
                project = self.projects.get(s.project)
                if project is not None:
                    inqname = self.queues.get(s.project)
                    # print("project queue:", s.project, inqname)
                    inq = build_queue('redis', qname=inqname)
                    inq.put_first(task)
                    inq.close()
                new_projects.append(s.project)
               
            self.db.commit()
            logging.debug("load new projects :%s"% str(new_projects))
            for project in new_projects:
                processor = self.processors.get(project)
                if processor is None or processor.status != 1:
                    self._load_processor(project)


            gevent.sleep(10)

    def do_processor(self, processor):
        processor.run()

    # def do_loader(self):
    #     try:
           
    #         while True:
    #             now = time.time()
    #             for k,project in self.projects.items():
    #                 if project.load_time > now:
    #                     continue
    #                 spider = self.spiders.get(project.name)
    #                 if spider is None or spider.status != START:
    #                     logging.warn("spider (%s) is not ready." % project.name)
    #                     print(spider, spider.status)
    #                     continue
    #                 taskq = self.queues.get(project.queue_name)
    #                 if (project.queue_name != 'common' and taskq.qsize() > 0) or (project.queue_name=='common' and taskq.qsize() >= 1000):
    #                     continue
                    
    #                 new_tasks = self._load_tasks(project.name)
    #                 tasks_size = len(new_tasks)
    #                 if tasks_size <= 0:
    #                     logging.info('project [%s] load no task' % project.name)
    #                     #project.load_time = now + 10*1000 
    #                     continue
    #                 else:
    #                     logging.info('project [%s] load %d tasks' % (project.name, tasks_size))
    #                 for task in new_tasks:
    #                     # print("put in queue", json.dumps(task))
    #                     taskq.put(task)

    #             else:
    #                 gevent.sleep(2)
    #     except Exception as e:
    #         logging.error("Scheduler Error!\n%s" % traceback.format_exc())
        

    def do_worker(self, project):

        try:
            # task = self.qin.get()
            taskq = self.queues.get(project.name)
            
            while True:

                try:
                    task = taskq.get()
                    if task == StopIteration or task == '':
                        logging.info("worker [%s] get none task, exit do worker" % (project.name))
                        break
                    if task is None:
                        gevent.sleep(2)
                        logging.info("worker [%s] get no task, sleep 2 seconds" % (project.name))
                        continue

                    logging.info("do worker get a task", task) 
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
        logging.debug("do fetch task: %s" % task)
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
            if st is None:
                return
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
        

