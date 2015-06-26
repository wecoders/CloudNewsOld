import re

from easyspider.spider import EasySpider
from easyspider.cron import every

class Spider(EasySpider):
    
    @every(crontab=["* * * */10 *", "* * */5 * *"])
    def on_start(self):
        print("douban spider start")
        self.fetch("http://movie.douban.com/", callback=self.index_movie)

    def index_movie(self, response):
        for each in response.doc('a[href^="http"]').items():
            print(each.attr.href)
            if re.match("http://movie.douban.com/subject/\d+/$", each.attr.href):
                self.fetch(each.attr.href, callback=self.detail_movie)
        # print(response.doc, response.url, response.origin_url)

    def detail_movie(self, response):
        print("detail movie:", response.url)
        return {"title": response.doc('h1').text()}