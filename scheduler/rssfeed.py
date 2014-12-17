import os
import feedparser
import re
import time
import calendar
import logging
logger = logging.getLogger("rssfeed.log")
from datetime import datetime

from news import session, delete_news,save_news,save_cache, update_sites,reset_news

from settings import load_config
import pytz

tz = pytz.timezone('Asia/Shanghai')

def fetch_feed(site, url, id_pattern=None):
	logger.debug("fetch %s"%site)
	feed = feedparser.parse(url)
	news_list = []
	for entry in feed['entries']:
		#print entry.keys()
		#print entry['id'], entry['published_parsed'], type(entry['published_parsed']),datetime.fromtimestamp(time.mktime(entry['published_parsed']))

		news = dict()
		# if id_pattern:
		# 	m = re.findall(id_pattern, entry['link'])
		# 	if len(m)>0:
		# 		news['newsId'] = m[0]
		# 		print m[0]
		# 	else:
		# 		news['newsId'] = entry['link']
		if entry.has_key('id'):
			news['newsId'] = entry['id']
		else:
			news['newsId'] = entry['link']
		news['site'] = site
		news['title'] = entry['title']
		news['subTitle'] = None
		news['sourceUrl'] = entry['link']
		news['voteCount'] = 0
		news['commentCount'] = 0
		news['url'] = entry['link']
		news['sorts'] = int(time.mktime(entry['published_parsed']))
		createAt = datetime.fromtimestamp(calendar.timegm(entry['published_parsed']), tz=tz)
		news['createAt'] = createAt.strftime("%Y-%m-%d %H:%M:%S")
		news_list.append(news)
		# print news['createAt'], entry['published'], entry['published_parsed']
	save_news(site, news_list)
	update_sites(site, datetime.now())

def run():
	logger.info("run feed new: %s"%datetime.now())
	config = load_config("rss.yaml")
	for site in config.sites:
		try:
			fetch_feed(site.name, site.feed)	
		except Exception, e:
			logger.error(e)



if __name__ == "__main__":
	run()

