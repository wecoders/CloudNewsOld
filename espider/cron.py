# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
import datetime
import calendar

MINUTE=0
HOUR=1
DAY=2
MONTH=3
WEEK=4
YEAR=5

CRON_RANGES = [
    (0, 59),
    (0, 23),
    (1, 31),
    (1, 12),
    (0, 6),
    #(1970, 2099),
]


def every(cron=[]):
    """
    cron = ["* * * * *", "* * */10 * 2"]
    """
    def wrapper(func):
        
        func.is_cronjob = True
        func.crons = []
        for c in cron:
            if isinstance(c, str):
                cols = c.split(' ')
                if len(cols) != 5:
                    continue
                m = cols[0]
                h = cols[1]
                d = cols[2]
                month = cols[3]
                week = cols[4]
                if week == "*":
                    #week优先
                    week = None

                cfg = CronConfig(m,h,d,month,week)
                func.crons.append(cfg)
        return func
    return wrapper


class CronConfig(object):
    def __init__(self, minute="*", hour="*", day="*", month="*", week=None):
        
        """
        week优先
        """
        if week is  None or week == "":
            self.day = self._parse_piece(DAY, day)
            self.week = []
        else:
            self.week = self._parse_piece(WEEK, week)
            self.day = []
        self.month = [] #self._parse_piece(MONTH, month)
        self.hour = self._parse_piece(HOUR, hour)
        self.minute = self._parse_piece(MINUTE, minute)

    def __str__(self):
        return "minute:"+str(self.minute)+" hour:"+str(self.hour)+" day:"+str(self.day)+" month:"+str(self.month)+" week:"+str(self.week)

    def _parse_piece(self, col, v):
        
        vals = []
        if v is None:
            return []
        if ',' in v:
            for a in v.split(','):
                vals.append(int(a))
            # print(map(a) for a in v.split(','))
        else:
            incr = 1
            start , end = CRON_RANGES[col]
            if '-' in v:
                start, end = v.split('-')
                start = int(start,10)
                end = int(end,10)
            elif v == '*':
                start, end= CRON_RANGES[col]
            elif '*/' in v:
                _, incr = v.split('/')
                incr = int(incr, 10)
            elif v == "" or v is None:
                start = end = 0
            else:
                start = int(v,10)
                end = int(v,10)
            # for i in range(start,end+1, incr):
            #     vals.append(i)
            vals = list(range(start,end+1, incr))
                
            if col == WEEK and 7 in vals:
                vals.discard(7)
                vals.append(0)

        return vals

class CronTab(object):
    """docstring for CronTab"""
    def __init__(self, config):
        super(CronTab, self).__init__()
        
        self.config = config
    
    def array_min_pos(self, arr, val):
        
        for i in range(0, len(arr)):
            if arr[i] >= val:
                return i-1
    def find_time(self, arr, val):
        try:
            pos = arr.index(val)
            return True
        except ValueError:
            return False

    def next_pos(self, arr, val):
        go_next = False
        try:
            pos = arr.index(val)
        except ValueError:
            if len(arr) == 0:
                # go_next = True
                print(arr, val, 0, True)
                return (0,True)
            pos = -1

        if val<arr[0]:
            pos = 0
            go_next = False
        elif val>arr[-1]:
            pos = 0
            go_next = True
        else:

            if pos < 0:
                pos = self.array_min_pos(arr,val)
            
            if pos < 0:
                pos = 0
            elif pos == len(arr):
                pos = 0
            elif pos == len(arr)-1:
                pos = 0 
                go_next = True
            else:
                pos = pos + 1
        # print(arr, val, pos, go_next)
        return (pos, go_next)

    def go_next_minute(self, future):
        pos, go_next = self.next_pos(self.config.minute, future.minute)
        future = future.replace(minute=self.config.minute[pos])
        return (future, go_next)

    def go_next_hour(self, future):
        pos, go_next = self.next_pos(self.config.hour, future.hour)
        future = future.replace(hour=self.config.hour[pos]) 
        return (future, go_next)

    def go_next_day(self, future):
        pos, go_next = self.next_pos(self.config.day, future.day)
        next_day = self.config.day[pos]
        max_day = calendar.monthrange(future.year, future.month)[1]
        if next_day>max_day:
            go_next = True
            next_day = self.config.day[0]
        future = future.replace(day=next_day)
        return (future, go_next)

    def add_next_month(self, future):
        month = future.month-1+1
        year = future.year+int(month/12)
        month = month % 12+1
        future = future.replace(year=year, month=month)# + datetime.timedelta(month=1)
        
        return future

    def next(self, nowtime=None):
        now = nowtime or datetime.datetime.now()
        if isinstance(now, (int,float)):
            now = datetime.datetime.fromtimestamp(now)
        minute_go_next = hour_go_next = day_go_next = week_go_next = False
        future = now.replace(second=0, microsecond=0)

        if not self.find_time(self.config.day, future.day):
            future, day_go_next = self.go_next_day(future)
            if day_go_next:
                future = self.go_next_month(future)

            future = future.replace(hour=self.config.hour[0], minute=self.config.minute[0])
            
        elif not self.find_time(self.config.hour, future.hour):
            future, hour_go_next = self.go_next_hour(future)
            if hour_go_next:
                future, _ = self.go_next_day(future)
            future = future.replace(minute=self.config.minute[0])
        else:
            future, minute_go_next = self.go_next_minute(future)
            if minute_go_next:
                future, hour_go_next = self.go_next_hour(future)
            if hour_go_next:
                if len(self.config.day) != 0:
                    future, day_go_next = self.go_next_day(future)
                    if day_go_next:
                        future = self.add_next_month(future)

                else: #week
                    pass
        delay = future - datetime.datetime(1970, 1, 1)
        return future, delay.days * 86400 + delay.seconds + delay.microseconds / 1000000.




        
