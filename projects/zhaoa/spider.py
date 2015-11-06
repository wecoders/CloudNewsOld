# -*- coding: utf-8 -*-
#!/usr/bin/env python
import re
from easyspider.spider import EasySpider
from easyspider.cron import every, config
from scrapy import Selector
import logging

class Spider(EasySpider):
    
    
    @config(age=60)
    def on_detail_page(self, response):
        if response.url == response.old_url:
            try:
                hxs = Selector(text=response.content)

                summary = hxs.xpath('//div[@class="card-summary-content"]/*').extract()
                content = []
                for ctx in summary:
                    text = clean_html_text(ctx)
                    content.append(text)
                content_text = " ".join(content)
                content_text=content_text.replace("[1]","")
                content_text=content_text.replace("[2]","")
                
                item_dict={}
                items = hxs.xpath('//div[@class="baseInfoWrap"]/div/div/*')
                
                for item in items:
                    title = item.xpath('./span/text()').extract()
                    title_value = item.xpath('./div/text()').extract()
                    print("key:value", to_value(title), to_value(title_value))
                    item_dict[to_value(title)] = to_value(title_value)
                
                item_dict['summary'] = content_text
                imgs = hxs.xpath('//div[@class="lemma-picture summary-pic"]/a/img/@src').extract()
                item_dict['logo'] = to_value(imgs)
                print(item_dict)
                # save_content(self.site.name, url, json.dumps(item_dict))
                # update_url(self.site.name, url, 200)
                return item_dict
            except Exception,e:
                # update_url(self.site.name, url, 500)
                logging.error(e)
        else:
            logging.warn("url %s ignore..." % (response.old_url))

