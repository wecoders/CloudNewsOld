# -*- coding: utf-8 -*-
#!/usr/bin/env python
import re
from easyspider.spider import EasySpider
from easyspider.cron import every, config

class Spider(EasySpider):
    
    @every(crontab=["*/30 * * * *"])
    def on_start(self):
        self.fetch("http://timyang.net/", callback=self.on_index_page)

    def is_useless(self, url):
        if re.match('http://timyang.net/category/', url) \
                or re.match('http://timyang.net/tag/', url) \
                or re.match('http://timyang.net/comments/', url):
            return True
        else:
            return False
    @config(age=60*24)
    def on_index_page(self, response):
        for each in response.doc('a[href^="http://timyang.net/"]').items():
            # print("%s\n" % each.attr.href)
            if self.is_useless(each.attr.href):
                pass
            elif re.match('http://timyang.net/page/', each.attr.href):
                self.fetch(each.attr.href, callback=self.on_date_page)
            elif re.match('http://timyang.net/\d+/\d+/$', each.attr.href):
                self.fetch(each.attr.href, callback=self.on_date_page)
            elif re.match('http://timyang.net/[a-z]+/[\w\-]+/$', each.attr.href):
                self.fetch(each.attr.href, callback=self.on_detail_page)
            
    @config(age=7*60*24)
    def on_date_page(self, response):
        for each in response.doc('a[href^="http://timyang.net/"]').items():
            if self.is_useless(each.attr.href):
                pass
            elif re.match('http://timyang.net/\d+/\d+/page/\d+/$', each.attr.href):
                self.fetch(each.attr.href, callback=self.on_date_page)
            elif re.match('http://timyang.net/[a-z]+/[\w\-]+/$', each.attr.href):
                self.fetch(each.attr.href, callback=self.on_detail_page)
            
            
    @config(priority=9)
    def on_detail_page(self, response):
        return {"title": response.doc('h2.posttitle>a').text()}

