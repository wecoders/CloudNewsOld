# -*- coding: utf-8 -*-
#!/usr/bin/env python
import re
from easyspider.spider import EasySpider
from easyspider.cron import every, config

class Spider(EasySpider):
    
    @every(crontab=["*/30 * * * *"])
    def on_start(self):
        self.fetch("http://blog.codingnow.com/", callback=self.on_index_page)

    @config(age=30)
    def on_index_page(self, response):
        for each in response.doc('a[href^="http://blog.codingnow.com"]').items():
            if re.match("http://blog.codingnow.com/\d+/\d+/\w+\.html$", each.attr.href):
                self.fetch(each.attr.href, callback=self.on_detail_page)
            if re.match("http://blog.codingnow.com/\d+/\d+/$", each.attr.href):
                self.fetch(each.attr.href, callback=self.on_index_page)
            
    @config(priority=9)
    def on_detail_page(self, response):
        return {"title": response.doc('h3').filter('.entry-header').text()}

