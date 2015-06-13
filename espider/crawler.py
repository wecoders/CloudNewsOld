# -*- coding: utf-8 -*-
#!/usr/bin/env python
import gevent
from gevent import monkey, queue
monkey.patch_all()

from .mq import build_queue

class EasyCrawler:
    def __init__(self, timeout=5, workers_count=5, min_capacity=10, pipeline_size=100, loop_once=False):

        self.spiders = load_spiders
        self.timeout = timeout
        self.loop_once = loop_once
        self.qin = build_queue("redis") 
        self.qout = build_queue("redis") 
        self.jobs = [gevent.spawn(self.do_scheduler)]
        self.jobs += [gevent.spawn(self.do_worker) for i in range(workers_count)]
        self.jobs += [gevent.spawn(self.do_pipeline)]
        self.job_count = len(self.jobs)
        self.lock = threading.Lock()

    def load_spiders(self):
        return []

    def start(self):
        gevent.joinall(self.jobs)

    def do_scheduler(self):
        try:
            #retry_count=0
            #self.qin.put({'url':self.spider.settings.before_run_url, 'is_target':0})
            #print "start crawl site %s" % (self.spider.settings.site)
            for spider in self.spiders:
                spider.prepare()
                
            while True:
                if self.q.qsize() < self.min_capacity:
                    for spider in self.spiders:
                        urls = spider.scheduler()

                        pass
                pass

            if self.spider.settings.require_login:
                res = self.spider.require_login()
                if res is None:
                    logging.error("do login error !!!!  %s"% self.spider.settings.site)
                    
            for url in self.spider.settings.start.urls:
                self.qin.put({'url':url, 'is_target':0})

            while True:
                if self.qin.qsize()< 2:
                    urls = []
                    try:
                        urls = self.spider.scheduler()  #  return a generator
                        if urls is None:
                            continue
                    except:
                        logging.error("Pipeline error!\n%s" % traceback.format_exc()) 

                    logging.debug("do scheduler urls size: %d" % len(urls))
                    size = 0
                    for url in urls:
                        size += 1
                        self.qin.put(url)
                    logging.debug( "do schedule size: %d, retry:%d, job count:%d" %(size, retry_count, self.job_count))
                    if size <= 0:
                        if retry_count >= 50:
                            print "restart crawl site %s" % (self.spider.settings.site)
                            retry_count = 0
                            self.spider.reset_urls()
                            for url in self.spider.settings.start.urls:
                                self.qin.put({'url':url, 'is_target':0})
                            
                        else:
                            retry_count += 1
                            sleep(2)
                    else:
                        retry_count = 0
                else:
                    sleep(3)

                if self.loop_once:
                    break;
                
        except Exception, e:
            logging.error("Scheduler Error!\n%s" % traceback.format_exc())
        finally:
            self.lock.acquire()
            try:
                for i in range(self.job_count - 2):
                    self.qin.put(StopIteration)

                self.job_count -= 1
            finally:
                logging.debug("Scheduler done, ======================== job count: %s" % self.job_count)
                self.lock.release()
            

    def do_worker(self):

        try:
            item = self.qin.get()
            while item != StopIteration:
                try:
                    #print item
                    res = self.spider.fetch(item)
                    if res != None:
                        #print res
                        new_page_urls = res['new_page_urls']
                        new_target_urls = res['new_target_urls']
                        
                        # for url in new_page_urls:
                        #     self.qin.put(url)
                        # for url in new_target_urls:
                        #     self.qin.put(url)
                        r = {}
                        r['url'] = item.get('url')
                        r['html'] = res['html']
                        r['content_type'] = res.get('content_type')
                        # r['content'] = res['content']
                        #logging.debug("html: === %s" % res['html'])
                        logging.debug("new page urls: === %s" % new_page_urls)
                        logging.debug("new target urls: === %s" % new_target_urls)
                        logging.debug("is target: %d, code: %d" % (item['is_target'], res['code']))

                        if item['is_target'] == 1 and res['code'] == 200:
                            self.qout.put(r)
                except:
                    logging.error("Worker error!\n%s" % traceback.format_exc())

                
                item = self.qin.get()
                
        finally:
            self.lock.acquire()
            self.job_count -= 1
            self.lock.release()
            logging.debug("Worker done, ==========================  job count: %s" % self.job_count)

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
        

