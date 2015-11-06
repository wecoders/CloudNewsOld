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



from easyspider.cron import CronConfig, CronTab, every

@every(crontab=["* * * */10 *", "* * */1 * 2"])
def run():
    print("run:")

class TestA(object):
    """docstring for TestA"""
    def __init__(self, arg):
        super(TestA, self).__init__()
        self.arg = arg

    @every(cron=["* * */5 * *", "* * */1 */2 3", "0 */2 * * *"])
    def run(self):
        print("")
        


if __name__ == '__main__':
    #config = CronConfig()
    config = CronConfig(minute="10,20,30,40,50", hour="1,2", day="*")
    #config = CronConfig(minute="1-10", hour="2-5", day="*/5", week="*/2")
    #config = CronConfig(minute="1-10", hour="2-5", day="*/5", week="")
    print(config)
    cron = CronTab(config)
    now = datetime.datetime.now()
    print(type(now))
    now = datetime.datetime.strptime('2015-06-13 20:38:01', "%Y-%m-%d %H:%M:%S")
    print(type(now))
    print(now, cron.next(now))
    now = datetime.datetime.strptime('2015-06-16 20:00:01', "%Y-%m-%d %H:%M:%S")
    print(now, cron.next(now))
    now = datetime.datetime.strptime('2015-06-16 20:52:01', "%Y-%m-%d %H:%M:%S")
    print(now, cron.next(now))
    now = datetime.datetime.strptime('2015-06-16 00:12:01', "%Y-%m-%d %H:%M:%S")
    print(now, cron.next(now))
    now = datetime.datetime.strptime('2015-06-16 00:52:01', "%Y-%m-%d %H:%M:%S")
    print(now, cron.next(now))
    now = datetime.datetime.strptime('2015-06-16 01:22:01', "%Y-%m-%d %H:%M:%S")
    print(now, cron.next(now))

    now = datetime.datetime.strptime('2015-06-16 01:52:01', "%Y-%m-%d %H:%M:%S")
    print(now, cron.next(now))
    
    now = datetime.datetime.strptime('2015-06-16 02:52:01', "%Y-%m-%d %H:%M:%S")
    print(now, cron.next(now))
    
    now = datetime.datetime.strptime('2015-06-30 02:52:01', "%Y-%m-%d %H:%M:%S")
    print(now, cron.next(now))
    
    now = datetime.datetime.strptime('2015-07-31 02:52:01', "%Y-%m-%d %H:%M:%S")
    print(now, cron.next(now))
    