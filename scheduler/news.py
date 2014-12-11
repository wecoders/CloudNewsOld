
import json
import redis
import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
import settings


engine = create_engine(settings.database)

session = sessionmaker()
session.configure(bind=engine)


Base = declarative_base()

pool = redis.ConnectionPool(host=settings.redis_host, port=settings.redis_port)
client =  redis.Redis(connection_pool=pool)


class NewsSite(Base):
    __tablename__ = 'news_site'
    id = Column(Integer, primary_key=True)
    uri = Column(String)
    name = Column(String)
    sorts = Column(Integer)
    create_at = Column(DateTime)


class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    site = Column(String)
    news_id = Column(String)
    title = Column(String)
    sub_title = Column(String)
    source_url = Column(String)
    url = Column(String)
    vote_count = Column(Integer)
    comment_count = Column(Integer)
    sorts = Column(Integer)
    create_at = Column(DateTime)

def delete_news(site_id):
	db = session()
	db.execute("delete from news where site = '%s'"%site_id)
	db.commit()
	db.close()

def reset_news(site_id, last_time, day):
	last_timestamp = int(time.mktime(last_time.timetuple()))
	db = session()
	db.execute("update news set sorts = %d where site = '%s' and create_at='%s'"%(last_timestamp, site_id, day))
	db.commit()
	db.close()


def save_news(site,news_list, page=None):
	db = session()
	for item in news_list:
		news_id = item['newsId']
		news =  db.query(News).filter_by(site=site, news_id=news_id).first()
		if news is None:
			news = News()

		news.site = item['site']
		news.title = item['title']
		news.sub_title = item.get('subTitle')
		news.source_url = item['sourceUrl']
		news.url = item['url']
		news.vote_count = item['voteCount']
		news.comment_count = item['commentCount']
		news.sorts = item['sorts']
		news.news_id = item['newsId']
		news.create_at = item['createAt']

		db.add(news)
	db.commit()
	db.close()
	return len(news_list)

def save_cache(site, news_list):
	size = len(news_list)
	i=0
	p = 1
	while i<size:
		if i+30 >= size:
			slide = news_list[i:]
		else:
			slide = news_list[i:i+30]
		res = json.dumps(slide)
		client.set('news:'+site+":"+str(p), res)
		p=p+1
		i=i+30
	key = 'news:'+site+":count"
	client.set(key, size)

def update_sites(name, now=None):
	print "update sites"
	if now is None:
		now = datetime.now()
	db = session()
	news_site = db.query(NewsSite).filter_by(uri=name).first()
	if news_site:
		print "site time: ", news_site.name, now
		news_site.create_at = now
		db.add(news_site)
		db.commit()
		db.close()
	else:
		print "update site error, site is None !!!"

