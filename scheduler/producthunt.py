
#https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty
import json
import requests
import re
from scrapy import Selector
from .fetch import fetch
from datetime import datetime
from news import session, delete_news,save_news, save_cache, update_sites

site_url = 'http://www.producthunt.com/'

Site="producthunt"



def fetch_news(url, page):
	res = fetch(url)
	if res['code'] != 200:
		return []
	html = res['html']
	#print html
	hxs = Selector(text=html)
	trs = hxs.xpath('//ul[@class="posts-group"]/li')
	cnt = len(trs)
	i=0
	logging.debug("fetch count: %d from %s" % (cnt, url))
	news_list = []
	for tr0 in trs:
		points = tr0.xpath('./div/span[@class="vote-count"]/text()').extract()
		title = tr0.xpath('./div[@class="url"]/a/text()').extract()
		sub_title = tr0.xpath('./div[@class="url"]/span/text()').extract()
		
		source_link = tr0.xpath('./div[@class="url"]/a/@href').extract()
		comments = tr0.xpath('./a[@class="view-discussion"]/p/text()').extract()
		comments_link = tr0.xpath('./a/@href').extract()

		if len(source_link) > 0:
			source_link = source_link[0]
			source_link = "http://www.producthunt.com" + source_link;
		
		if len(title)>0:
			title = title[0]
		else:
			title = None

		if len(sub_title)>0:
			sub_title = sub_title[0]
			
		if len(points)>0:
			points = points[0]
		else:
			points = 0
		if len(comments)>0:
			comments = comments[0]
		else:
			comments = 0

		if len(comments_link)>0:
			comments_link = comments_link[0]
			comments_link = "http://www.producthunt.com"+comments_link

		if title is None:
			continue

		news = dict()
		news['site'] = Site
		news['title'] = title
		news['subTitle'] = sub_title
		news['sourceUrl'] = source_link
		news['voteCount'] = points
		news['commentCount'] = comments
		news['url'] = comments_link
		# print link, title, points, comments, news_link
		print news
		news_list.append(news)
		i+=1
	save_news(Site,news_list,page)
	return news_list


def run():
	delete_news(Site)
	news=[]
	lst = fetch_news(site_url, 1)
	if lst is not None:
		news.extend(lst)
	lst = fetch_news("http://www.producthunt.com/?page=2", 2)
	if lst is not None:
		news.extend(lst)

	save_cache(Site, news)
	update_sites(Site, datetime.now())


