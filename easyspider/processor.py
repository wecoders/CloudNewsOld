import time
import logging
import traceback
import gevent
import json
import datetime

from .utils import merge_cookie, import_object

from .fetcher import Fetcher
from .db import Session, ScopedSession, SpiderProject, SpiderTask, SpiderScheduler,SpiderResult
from .mq import build_redis_queue

class EasyProcessor:
    def __init__(self, project, spider, qname):
        self.project = project
        self.spider = spider
        self.fetcher = Fetcher()
        self.qname = qname #'q_'+project+time.time()

        self.queue = build_redis_queue(qname=qname)
        self.db = Session()
        self.status = 1


    def run(self):
        try:
            fail_count = 0
            while True:
                try:
                    if self.status != 1:
                        # self.close()
                        break
                    task = self.queue.get()
                    if task == '':
                        # self.clear_queue()
                        # self.close()
                        logging.info("processor %s get empty task." % self.project)
                        break
                    if task is None:
                        fail_count += 1
                        if fail_count > 1000:
                            # self.close()
                            logging.info("processor %s try get task(empty) counts from queue(%s) > 10." % (self.project,self.qname))
                            # break
                            gevent.sleep(10)
                        else:
                            tasks = self.load_tasks()
                            if len(tasks)<=0:
                                logging.debug("load project(%s) empty tasks from database" % (self.project))
                                gevent.sleep(10)
                    else:
                        fail_count = 0
                        self.do_fetch(task)
                except:
                    logging.error("run processor error!\n%s" % traceback.format_exc())
        except:
            logging.error("Worker error!\n%s" % traceback.format_exc())
        logging.info("processor %s exit." % self.project)
        self.close()
    def close(self):
        self.db.close()
        self.queue.close()
        self.status = -1

    def clear_queue(self):
        while True:
            task = self.queue.get()
            if task is None:
                break
            if task == '':
                pass
            task_id = task.get('task_id')
            dbtask = self.db.query(SpiderTask).filter(SpiderTask.task_id==task_id).first()
            dbtask.status = 0
            self.db.add(dbtask)
            self.db.commit()


    def do_fetch(self, task):
        logging.debug("do fetch task: %s", json.dumps(task))
        
        headers = self.spider.config.headers
        url = task.get('url')
        task_id = task.get('task_id')
        if url.startswith('data://'):
            callback = url[7:] # task.get('callback')
            if callback is not None and callback != '':
                logging.debug("call callback %s" % callback)
                callback_func = getattr(self.spider, callback)
                if callback_func:
                    callback_func()
            
        else:
            response = self.fetcher.fetch(self.spider, task, headers)
            if 'set-cookie' in response:
                new_cookie = response['set-cookie']
                old_cookie = headers.get('Cookie', None)
                headers['Cookie'] = merge_cookie(new_cookie, old_cookie)

            result_code = response['code']
            if 'result' in response:
                res = response['result']
                if 'code' in res:
                    result_code = res['code']
                sr = self.db.query(SpiderResult).filter_by(task_id=task_id).first()
                if sr is None:
                    sr = SpiderResult()
                sr.project = task.get('project')
                sr.task_id = task_id
                sr.url = url
                sr.content = json.dumps(res)
                sr.create_at = datetime.datetime.now()
                self.db.add(sr)
            st = self.db.query(SpiderTask).filter_by(task_id=task_id).first()
            if st is None:
                return
            st.status = result_code
            st.last_time = time.time()
            self.db.add(st)
            self.db.commit()
            self.db.close()

    def load_tasks(self):
        # db = Session()
        tasks = self.db.query(SpiderTask).filter(SpiderTask.project==self.project, SpiderTask.status==0).order_by('priority').limit(30).all()
        
        new_tasks = []
        if len(tasks)<=0:
            # logging.debug("load project(%s) tasks is empty." % (self.project))
            self.db.close()
            return new_tasks

        for task in tasks:
            task.status = 1
            self.db.add(task)
            # db.commit()
            new_task={}
            new_task['id'] = task.id
            new_task['task_id'] = task.task_id
            new_task['project'] = task.project
            new_task['url'] = task.url
            new_task['callback'] = task.callback
            new_tasks.append(new_task)
        self.db.commit()
        self.db.close()
        for task in new_tasks:
            self.queue.put(task)
        return new_tasks