import json
import requests
import re
import logging
from datetime import datetime, timedelta

import time

from news import delete_news,save_news, save_cache, update_sites,reset_news

from .fetch import fetch

site_url = 'https://api.producthunt.com/v1/posts'

Site="ProductHunt"




def fetch_data(date):
    last_time = datetime(date.year, date.month, date.day, 23, 59,59)
    first_time = datetime(date.year, date.month, date.day, 0, 0,1)
    day = date.strftime('%Y-%m-%d')
    url = "%s?day=%s" % (site_url, day)
    headers = {}
    headers['Authorization']='Bearer 2c83f63e37eb54010822cf3d90e282a940e2ee74a7dfaa486636b24e5c96cee2'
    headers['Accept'] = 'application/json'
    headers['Content-Type'] = 'application/json'
    res = fetch(url, headers)
    if res['code'] != 200:
        return

    json_html = res['html']
    try:
	    json_data = json.loads(json_html)
	    posts = json_data.get('posts')
	    if posts is None:
	        logging.error("PH fetch data json response has no posts data. posts == None")
	        return
	    logging.debug("fetch count: %d from %s" % (len(posts), url))
	    news_list = []
	    for post in posts:
	        news = dict()
	        news['site'] = Site
	        news['newsId'] = post.get('id')
	        news['title'] = post.get('name')
	        news['subTitle'] = post.get('tagline')
	        news['sourceUrl'] = post.get('redirect_url')
	        news['voteCount'] = post.get('votes_count')
	        news['commentCount'] = post.get('comments_count')
	        news['url'] = post.get('discussion_url')
	        news['createAt'] = day #post.get('created_at')
	        news_list.append(news)

	    if len(news_list)<=0:
	        return

	    last_timestamp = int(time.mktime(last_time.timetuple()))
	    for news in news_list:
	        news['sorts'] = last_timestamp
	        last_timestamp -= 1

	    if len(news_list)>0:
	        reset_news(Site, first_time, day=day)
	    save_news(Site, news_list)

    except Exception, e:
        logging.error(e)
        print e
    

def run():
    now = datetime.now()
    yesterday = now - timedelta(hours=24)
    fetch_data(now)
    fetch_data(yesterday)

    update_sites(Site, now)



