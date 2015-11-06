# -*- coding: utf-8 -*-
#!/usr/bin/env python
import re
from easyspider.spider import EasySpider
from easyspider.cron import every, config

class Spider(EasySpider):
    
    @every(crontab=["*/30 * * * *"])
    def on_start(self):
        self.fetch("http://www.blogjava.net/", callback=self.on_index_page)

    @config(age=30)
    def on_index_page(self, response):
        for each in response.doc('a[href^="http://www.blogjava.net"]').items():
            if re.match("http://www.blogjava.net/\w+/\w+/\d+/\d+/\d+/\d+\.html$", each.attr.href):
                self.fetch(each.attr.href, callback=self.on_detail_page)
            
    @config(priority=9)
    def on_detail_page(self, response):
        return {"title": response.doc('h1').text(), "url": response.url}

