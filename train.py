# -*- coding: utf-8 -*-


from easyspider.db import SpiderResult
import json

reslist = SpiderResult.query.filter(SpiderResult.project=='infoq').all()

fp = open("infoq.txt", "w+")
for res in reslist:
    content_json = json.loads(res.content)
    title = content_json['title']
    print(res.url, title)
    fp.write("%s" % title)
    fp.write("\n")
fp.close()