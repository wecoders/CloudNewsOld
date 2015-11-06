# -*- coding: utf-8 -*-
#!/usr/bin/env python

from gevent import monkey
monkey.patch_all()


import os
import datetime
import sys

PROJDIR = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.split(PROJDIR)[0]
try:
    import site
    site.addsitedir(PROJDIR)
    # print(sys.path)
    import easyspider
    print('Start easyspider testing: %s' % PROJDIR)
except ImportError:
    print('import error easyspider')
    exit(-1)

import logging
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(thread)d:%(module)s:%(funcName)s:%(lineno)d:%(message)s', level=logging.DEBUG)

# logging.basicConfig(filename='spider.log',format='%(levelname)s:%(thread)d:%(message)s', level=logging.DEBUG)

#print('run')
# from easyspider.utils import  TestClass
from easyspider.crawler import EasyCrawler
from easyspider.db import SpiderProject
from easyspider.utils import md5str, load_module
from easyspider.config import import_config
from easyspider.fetcher import Fetcher
spider_name = sys.argv[1]
print("run spider:", spider_name)
# projects =  SpiderProject.load_projects() #query.filter_by(status=1).all()
# spiders = {}
# for project in projects:
#     try:
#         spider = import_object("projects.%s.spider.Spider"% (project.name))
#         config = import_config("projects.%s.project.yaml" % (project.name))
#         spider.config = config
#         spiders[project.name] = spider
        
#     except Exception as e:
#         raise e


#ec = EasyCrawler()
#ec.start()
def fetch_wrapper(url, callback):
    print("fetch wrapper url:", url, getattr(callback, '__name__'))
    task_id = md5str(url)
    task_cfg = {}
    task_cfg['task_id'] = task_id
    task_cfg['project'] = spider_name
    task_cfg['url'] = url
    if callback is not None:
        task_cfg['callback'] = getattr(callback, '__name__')
        if hasattr(callback, '_age'):
            task_cfg['age'] = callback._age
        if hasattr(callback, '_priority'):
            task_cfg['priority'] = callback._priority

    return task_cfg


spider_cls = load_module("projects/%s/spider.py" % spider_name)
config = import_config("projects/%s/project.yaml" % (spider_name))
spider = spider_cls()
spider.config = config
spider.fetch = fetch_wrapper


url="http://blog.jobbole.com/93689/"
task = fetch_wrapper(url=url, callback=spider.on_detail_page)
print(task)
fetcher = Fetcher()
response = fetcher.fetch(spider, task, spider.config.headers)
print("response:", response.get('result', None))




