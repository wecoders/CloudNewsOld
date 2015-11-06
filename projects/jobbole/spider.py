# -*- coding: utf-8 -*-
#!/usr/bin/env python
import re
import logging
from easyspider.spider import EasySpider
from easyspider.cron import every, config

class Spider(EasySpider):
    
    @every(crontab=["*/30 * * * *"])
    def on_start(self):
        self.fetch("http://blog.jobbole.com/category/programmer", callback=self.on_index_page)
        self.fetch("http://blog.jobbole.com/category/it-tech", callback=self.on_index_page)
        self.fetch("http://blog.jobbole.com/category/design", callback=self.on_index_page)

    #age: minute
    @config(age=30*60) #age:30minute
    def on_index_page(self, response):
        logging.debug("call spider on_index_page")
        for each in response.doc('a[href^="http://blog.jobbole.com/"]').items():
            #print(each.attr.href)
            if re.match("http://blog.jobbole.com/category/\w+/page/\d+/$", each.attr.href):
                self.fetch(each.attr.href, callback=self.on_index_page)
                # print(each.attr.href)
            if re.match("http://blog.jobbole.com/\d+/$", each.attr.href):
                self.fetch(each.attr.href, callback=self.on_detail_page)
                # new_url = each.attr.href
                # new_title = each.text()
                #self.on_result({'url': new_url, 'content': {'title': new_title}})


    @config(age=60*24*7, priority=9) #age:7days
    def on_detail_page(self, response):
        return {"title": response.doc('h1').text()}

