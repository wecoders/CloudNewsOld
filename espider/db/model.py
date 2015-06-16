# -*- coding: utf-8 -*-
#!/usr/bin/env python
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
 
from .mysql import Session

Base = declarative_base()

class BaseMixin():
    query =  Session.query_property()

class SpiderProject(Base, BaseMixin):
    __tablename__ = 'spider_project'
    id = Column(Integer, primary_key=True)
    project = Column(String)
    enable = Column(Integer)
    process = Column(String)
    create_at = Column(DateTime, default=datetime.datetime.now())

Project = SpiderProject


class SpiderTask(Base, BaseMixin):
    __tablename__ = 'spider_task'
    id = Column(Integer, primary_key=True)
    project = Column(String)
    task_id = Column(String)
    url = Column(String)
    process = Column(String)
    priority = Column(Integer)
    next_time = Column(Integer)
    last_time = Column(Integer)
    status_code = Column(Integer)
    result = Column(String)
    create_at = Column(DateTime, default=datetime.datetime.now())

Task = SpiderTask


class SpiderScheduler(Base, BaseMixin):
    __tablename__ = 'spider_scheduler'
    id = Column(Integer, primary_key=True)
    project = Column(String)
    task_id = Column(String) #data://project/on_start
    url = Column(String) # data://on_start   http://
    process = Column(String) #{callback: ''}
    priority = Column(Integer)
    next_time = Column(Integer)
    last_time = Column(Integer)
    create_at = Column(DateTime, default=datetime.datetime.now())


class SpiderResult(Base, BaseMixin):
    __tablename__ = 'spider_result'
    id = Column(Integer, primary_key=True)
    project = Column(String)
    task_id = Column(String)
    url = Column(String)
    content = Column(String)
    create_at = Column(DateTime, default=datetime.datetime.now())

Result = SpiderResult


