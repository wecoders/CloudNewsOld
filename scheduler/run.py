
import os
import sys
import datetime
import logging

logging.basicConfig(filename="scheduler.log", format='%(asctime)s:%(levelname)s:%(thread)d:%(message)s', level=logging.DEBUG)


PROJDIR = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.split(PROJDIR)[0]
try:
    # 
    import site
    site.addsitedir(PROJDIR)
    site.addsitedir(ROOTDIR)
    
except ImportError:
    print('Development of keepcd')



from hackernews import run as hackernews_run
from producthunt_api import run as producthunt_run
from designernews import run as designernews_run

from apscheduler.schedulers.blocking import BlockingScheduler
from subprocess import call

def run_rss():
	call(['/usr/bin/python', os.path.join(PROJDIR, 'rssfeed.py')])
	# os.sys("/usr/bin/python scheduler/rssfeed.py")


scheduler = BlockingScheduler()

now = datetime.datetime.utcnow()
now = now + datetime.timedelta(seconds=10)
# scheduler.add_job(hackernews_run,'interval', minutes=10,  id='hackernews', next_run_time=now)
# scheduler.add_job(producthunt_run,'interval', minutes=10,  id='producthunt', next_run_time=now)
# scheduler.add_job(designernews_run,'interval', minutes=10,  id='designernews', next_run_time=now)
scheduler.add_job(run_rss,'interval', minutes=10,  id='rssfeed', next_run_time=now)

scheduler.start()

# run_rss()

# from scheduler.news import update_sites

# update_sites('hackernews')

# hackernews_run()
# producthunt_run()
# designernews_run()
