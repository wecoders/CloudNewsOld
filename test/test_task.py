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

from easyspider.db import SpiderTask
from easyspider.db import Session , ScopedSession   
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session
engine = create_engine("mysql://root:admin@localhost/spider?charset=utf8")
scopedsession = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

#SpiderTask.query.filter(SpiderTask.project=='test').all()

db = Session()

db.query(SpiderTask).filter(SpiderTask.project=='test').all()

ScopedSession = scoped_session(sessionmaker())



q = scopedsession.query_property()
q2 = scopedsession.query_property()
print("scoped session", q, q==q2)


class Bar(object):
    """docstring for Bar"""
    def __init__(self):
        super(Bar, self).__init__()
        
class Foo(object):
    """docstring for foo"""
    a=1
    b=[]
    c=None
    q=None
    def __init__(self):
        super(Foo, self).__init__() 
        
print(Foo.a, Foo.b, Foo.c, Foo.q)
Foo.a = 2
Foo.b.append(1)
Foo.c = "ok"
Foo.q = scopedsession.query_property()
print(Foo.a, Foo.b, Foo.c, Foo.q)
f = Foo()
f.a = 3
f.b.append(2)
f.c = "no"
print(Foo.a, Foo.b, Foo.c)
print(f.a, f.b, f.c)


class SpiderProject(Base):
    query = scopedsession.query_property()
    __tablename__ = 'spider_project'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    a = ""

    @classmethod
    def q(cls):
        qr = scopedsession.query_property()
        print("get query", qr)
        return qr
print(q)
SpiderProject.a = "ok"
SpiderProject.query = q
# print(SpiderProject.a, SpiderProject.query)
# sp = SpiderProject()
# print(sp.query)
# print SpiderProject.q()
# after mappers are defined
# result = SpiderProject.query.filter(SpiderProject.name=='douban').all()
# print(result[0].name)

print(int(10))