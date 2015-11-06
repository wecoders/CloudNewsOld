import os
import datetime



PROJDIR = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.split(PROJDIR)[0]
try:
    #
    import site
    site.addsitedir(ROOTDIR)
    import easyspider
    print('Start easyspider testing: %s' % ROOTDIR)
except ImportError:
    print('import error easyspider')


from easyspider.cron import CronJob



job = CronJob(["*/60 */2 * * *"])
now = datetime.datetime.now()
delay = now - datetime.datetime(1970, 1, 1)
deltas = delay.days * 86400 + delay.seconds + delay.microseconds / 1000000.
print(delay,deltas,datetime.datetime.utcfromtimestamp(deltas))
next_time = job.next(now)

print(now, next_time, datetime.datetime.utcfromtimestamp(next_time))

job2 = CronJob(['*/5 * * * *'])
now2 = datetime.datetime.strptime('2015-06-30 17:00:34', "%Y-%m-%d %H:%M:%S")
next_time = job2.next(now2)
print(now2, next_time, datetime.datetime.utcfromtimestamp(next_time))
