# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
import os

project_name = sys.argv[1]
print("create project: %s" % project_name)

filename = "projects/%s/spider.py" % project_name
if not os.path.exists(os.path.dirname(filename)):
    os.makedirs(os.path.dirname(filename))

spider="""# -*- coding: utf-8 -*-
#!/usr/bin/env python
import re
from easyspider.spider import EasySpider
from easyspider.cron import every, config

class Spider(EasySpider):
    
    @every(crontab=["*/30 * * * *"])
    def on_start(self):
        self.fetch("http://www.%s.com/", callback=self.on_index_page)

    #age: minute
    @config(age=30*60) #age:30minute
    def on_index_page(self, response):
        for each in response.doc('a[href^="http://www.%s.com"]').items():
            self.fetch(each.attr.href, callback=self.on_detail_page)
            
    @config(age=60*24*7, priority=9) #age:7days
    def on_detail_page(self, response):
        return {"title": response.doc('h1').text()}

"""%(project_name, project_name)

project_config="""project: "%s"
group: "default"
enable: "true"
"""%project_name

if not os.path.exists(filename):
    with open(filename, "w+") as fp:
        fp.write(spider)
else:
    print("path %s already exists." % (filename))

config_filename="projects/%s/project.yaml"%project_name
if not os.path.exists(config_filename):
    with open(config_filename, "w+") as fp:
        fp.write(project_config)

init_filename="projects/%s/__init__.py"%project_name
if not os.path.exists(init_filename):
    with open(init_filename, "w+") as fp:
        fp.write("")


from easyspider.db import SpiderProject, Session

db = Session()

project = SpiderProject.query.filter_by(name=project_name).first()
if project is None:
    project = SpiderProject()
    project.name = project_name
    project.status = 0
    project.process = '{}'
    project.queue_name= project_name
    db.add(project)
    db.commit()


