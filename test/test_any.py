
MINUTE=0
HOUR=1
DAY=2
MONTH=3
WEEK=4
YEAR=5


_increments = [
    lambda *a: MINUTE,
    lambda *a: HOUR,
    lambda *a: DAY,
    None,
    lambda *a: DAY,
    None,
    lambda dt,x: dt.replace(minute=0),
    lambda dt,x: dt.replace(hour=0),
    lambda dt,x: dt.replace(day=1) if x > DAY else dt,
    lambda dt,x: dt.replace(month=1) if x > DAY else dt,
    lambda dt,x: dt,
]


print(_increments[0]())

