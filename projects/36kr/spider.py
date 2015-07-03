# -*- coding: utf-8 -*-
#!/usr/bin/env python
import re
from easyspider.spider import EasySpider
from easyspider.cron import every, config

class Spider(EasySpider):
    
    @every(crontab=["* * * * *"])
    def on_start(self):
        self.fetch("http://www.36kr.com/", callback=self.on_index_page)

    @config(age=1)
    def on_index_page(self, response):
        for each in response.doc('a[href^="http://36kr.com/p/"]').items():
            self.fetch(each.attr.href, callback=self.on_detail_page)
    @config(priority=9)
    def on_detail_page(self, response):
        return {"title": response.doc('h1').text()}

