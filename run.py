
import os
import sys
import datetime
import logging

logging.basicConfig(filename="scheduler.log", format='%(levelname)s:%(thread)d:%(message)s', level=logging.DEBUG)


PROJDIR = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.split(PROJDIR)[0]
try:
    # 
    import site
    site.addsitedir(ROOTDIR)
except ImportError:
    print('Development of keepcd')



from scheduler.hackernews import run as hackernews_run
from scheduler.producthunt_api import run as producthunt_run
from scheduler.designernews import run as designernews_run
from scheduler.rssfeed import run as rss_run

from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

now = datetime.datetime.utcnow()
now = now + datetime.timedelta(seconds=10)
scheduler.add_job(hackernews_run,'interval', minutes=6,  id='hackernews', next_run_time=now)
scheduler.add_job(producthunt_run,'interval', minutes=6,  id='producthunt', next_run_time=now)
scheduler.add_job(designernews_run,'interval', minutes=6,  id='designernews', next_run_time=now)
scheduler.add_job(rss_run,'interval', minutes=6,  id='rssfeed', next_run_time=now)

scheduler.start()

# from scheduler.news import update_sites

# update_sites('hackernews')

# hackernews_run()
# producthunt_run()
# designernews_run()
