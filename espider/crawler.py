# -*- coding: utf-8 -*-
#!/usr/bin/env python
import gevent
from gevent import monkey, queue
monkey.patch_all()

from .utils import merge_cookie
from .mq import build_queue
from .fetcher import Fetcher

class EasyCrawler:
    def __init__(self, timeout=5, workers_count=5, min_capacity=10, pipeline_size=100, loop_once=False):

        self.spiders = load_spiders
        self.timeout = timeout
        self.loop_once = loop_once
        self.qin = build_queue("redis") 
        # self.qout = build_queue("redis") 
        self.jobs = [gevent.spawn(self.do_scheduler)]
        self.jobs += [gevent.spawn(self.do_task)]
        self.jobs += [gevent.spawn(self.do_worker) for i in range(workers_count)]
        # self.jobs += [gevent.spawn(self.do_pipeline)]
        self.job_count = len(self.jobs)
        self.lock = threading.Lock()
        self.fetcher = Fetcher()

    def load_spiders(self):
        spiders = [] #load from projects
        for spider in spiders:
                spider.prepare()
        return {}

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
        

    def do_task(self):
        try:
            #retry_count=0
            #self.qin.put({'url':self.spider.settings.before_run_url, 'is_target':0})
            #print "start crawl site %s" % (self.spider.settings.site)
            
                
            while True:
                if self.q.qsize() < self.min_capacity:
                    for project in self.projects:
                        tasks = self.load_tasks(project)
                        for task in tasks:
                            self.qin.put(task)
                        
                

            # if self.spider.settings.require_login:
            #     res = self.spider.require_login()
            #     if res is None:
            #         logging.error("do login error !!!!  %s"% self.spider.settings.site)
                    
            

            # while True:
            #     if self.qin.qsize()< 2:
            #         urls = []
            #         try:
            #             urls = self.spider.scheduler()  #  return a generator
            #             if urls is None:
            #                 continue
            #         except:
            #             logging.error("Pipeline error!\n%s" % traceback.format_exc()) 

            #         logging.debug("do scheduler urls size: %d" % len(urls))
            #         size = 0
            #         for url in urls:
            #             size += 1
            #             self.qin.put(url)
            #         logging.debug( "do schedule size: %d, retry:%d, job count:%d" %(size, retry_count, self.job_count))
            #         if size <= 0:
            #             if retry_count >= 50:
            #                 print "restart crawl site %s" % (self.spider.settings.site)
            #                 retry_count = 0
            #                 self.spider.reset_urls()
            #                 for url in self.spider.settings.start.urls:
            #                     self.qin.put({'url':url, 'is_target':0})
                            
            #             else:
            #                 retry_count += 1
            #                 sleep(2)
            #         else:
            #             retry_count = 0
            #     else:
            #         sleep(3)

            #     if self.loop_once:
            #         break;
                
        except Exception, e:
            logging.error("Scheduler Error!\n%s" % traceback.format_exc())
        finally:
            pass
            # self.lock.acquire()
            # try:
            #     for i in range(self.job_count - 2):
            #         self.qin.put(StopIteration)

            #     self.job_count -= 1
            # finally:
            #     logging.debug("Scheduler done, ======================== job count: %s" % self.job_count)
            #     self.lock.release()
            

    def do_worker(self):

        try:
            task = self.qin.get()
            while task != StopIteration:
                try:
                    self.do_fetch(task)
                except:
                    logging.error("Worker error!\n%s" % traceback.format_exc())

                
                task = self.qin.get()
                
        finally:
            # self.lock.acquire()
            # self.job_count -= 1
            # self.lock.release()
            logging.debug("Worker done, ==========================  job count: %s" % self.job_count)

    
    def do_fetch(self, task):
        project = task['project']
        spider = self.spiders.get(project)
        headers = spider.headers
        response = self.fetcher.fetch(spider, task, headers)
        if 'set-cookie' in response:
            new_cookie = response['set-cookie']
            old_cookie = headers.get('Cookie', None)
            headers['Cookie'] = merge_cookie(new_cookie, old_cookie)

    def do_pipeline(self):
        pipeline_size = 0
        while self.job_count > 1 or not self.qout.empty():
            sleep(self.timeout)
            logging.debug("pipeline sleep, job count: %d" % self.job_count)
            try:
                results = []
                try:
                    i=0
                    while i<2:
                        i+=1
                        pipeline_size += 1
                        results.append(self.qout.get_nowait())
                        
                    if len(results) > 0:
                        self.spider.pipeline(results)
                except queue.Empty:
                    if len(results) > 0:
                        self.spider.pipeline(results)
            except:
                logging.error("Pipeline error!\n%s" % traceback.format_exc()) 
        

