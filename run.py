# -*- coding: utf-8 -*-
#!/usr/bin/env python

from gevent import monkey
monkey.patch_all()


import os
import datetime
import sys
from easyspider.utils import import_object

PROJDIR = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.split(PROJDIR)[0]
try:
    import site
    site.addsitedir(PROJDIR)
    print(sys.path)
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


ec = EasyCrawler()
ec.start()

