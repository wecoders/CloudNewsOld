# -*- coding: utf-8 -*-
#!/usr/bin/env python
import re
from easyspider.spider import EasySpider
from easyspider.cron import every

class Spider(EasySpider):
    
    @every(crontab=["* 0 */1 * *"])
    def on_start(self):
        self.fetch("http://project.com/", callback=self.on_index_page)

    def on_index_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            self.fetch(each.attr.href, callback=self.on_detail_page)

    def on_detail_page(self, response):
        return {"title": response.doc('h1').text()}

