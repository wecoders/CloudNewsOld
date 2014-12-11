
#https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty
import json
import requests
import re
import logging
from datetime import datetime, timedelta
import time
from scrapy import Selector
from .fetch import fetch
from news import session, delete_news,save_news,save_cache, update_sites,reset_news

hackernews_url = 'https://news.layervault.com/'

Site="designernews"



def fetch_news(url, news_list):
	res = fetch(url)
	if res['code'] != 200:
		return []
	html = res['html']
	#print html
	hxs = Selector(text=html)
	lis = hxs.xpath('//div[@class="Content"]/div[@class="InnerPage"]/ol/li')
	cnt = len(lis)
	i=0
	logging.debug("fetch count: %d from %s" % (cnt, url))
	for li in lis:
		source_link = li.xpath('./a[@class="StoryUrl"]/@href').extract()
		title = li.xpath('./a[@class="StoryUrl"]/@story_title').extract()
		sub_title = li.xpath('./a/span/text()').extract()
		 
		points = li.xpath('./div[@class="Below"]/span/text()').extract()

		comments = li.xpath('./div[@class="Below"]/span/a/text()').extract()
		comments_link = li.xpath('./div[@class="Below"]/span/a/@href').extract()
		
		nid = None
		if len(source_link)>0:
			#print source_link
			m = re.findall('(\d+)', source_link[0])
			if len(m)>0:
				nid = m[0]
		if nid is None:
			continue


		if len(source_link) > 0:
			source_link = source_link[0]
		else:
			source_link=None
		if len(title)>0:
			title = title[0]
		else:
			title = None

		if len(sub_title)>0:
			sub_title = sub_title[0]
		else:
			sub_title = None

		if len(points)>0:
			m = re.findall('(\d+) point', points[0])
			if len(m)>0:
				points = m[0]
			else:
				points = 0
		else:
			points = 0

		if len(comments)>0:
			m = re.findall('(\d+)', comments[0])
			if len(m)>0:
				comments = m[0]
			else:
				comments = 0
		else:
			comments = 0

		if len(comments_link)>0:
			comments_link = comments_link[0]
			comments_link = "https://news.layervault.com"+ comments_link
		else:
			comments_link = None


		
		news = dict()
		news['site'] = Site
		news['newsId'] = nid
		news['title'] = title
		news['subTitle']  = sub_title
		news['sourceUrl'] = source_link
		news['voteCount'] = points
		news['commentCount'] = comments
		news['url'] = comments_link
		news['createAt'] = None
		# print link, title, points, comments, news_link
		#print news
		news_list.append(news)
		

	
	return news_list

def run():
	# delete_news(Site)
	news_list = []
	fetch_news("https://news.layervault.com/", news_list)
	fetch_news("https://news.layervault.com/p/2", news_list)
	fetch_news("https://news.layervault.com/p/3", news_list)
	

	now = datetime.now()
	last_time = datetime(now.year, now.month, now.day, 23, 59,59)
	first_time = datetime(now.year, now.month, now.day, 0, 0,1)

	last_timestamp = int(time.mktime(last_time.timetuple()))
	for news in news_list:
		news['sorts'] = last_timestamp
		last_timestamp -= 1

	
	save_news(Site,news_list)
	update_sites(Site)
	#save_cache(Site, news_list)

