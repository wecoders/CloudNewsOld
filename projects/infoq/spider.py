# -*- coding: utf-8 -*-
#!/usr/bin/env python
import re
import logging
from pyquery import PyQuery

from easyspider.spider import EasySpider
from easyspider.cron import every, config

class Spider(EasySpider):
    
    @every(crontab=["*/30 * * * *"])
    def on_start(self):
        self.fetch("http://www.infoq.com/cn/news", callback=self.on_index_page)

    @config(age=30*60)
    def on_index_page(self, response):
        logging.debug("infoq index page, %s" % response.url)
        for each in response.doc('a[href^="/cn/news/"]').items():
            logging.debug(each.attr.href)
            if re.match('/cn/news/\d+/\d+/[a-zA-Z0-9\-]+$', each.attr.href):
                logging.debug("matched url: %s" % each.attr.href)
                self.fetch("%s%s" % ("http://www.infoq.com", each.attr.href), callback=self.on_detail_page)
            if re.match('/cn/news/\d+$', each.attr.href):
                self.fetch("%s%s" % ("http://www.infoq.com", each.attr.href), callback=self.on_index_page)
            
    @config(priority=9)
    def on_detail_page(self, response):
        li = response.doc('div').filter('.random_links').find('ul').find('li')
        tags = []
        findtag = False
        for i in li:
            v = PyQuery(i).text()
            # print(v)
            if findtag == True:
                tags.append(v)
            if v == '专栏':
                findtag = True
        # print(tags)
        return {"title": response.doc('h1').text(), 'category': tags}

