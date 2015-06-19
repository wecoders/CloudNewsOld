# -*- coding: utf-8 -*-
#!/usr/bin/env python
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
 
from .mysql import Session

class BaseMixin():
    query =  Session.query_property()

Base = declarative_base()

class SpiderProject(Base):
    __tablename__ = 'spider_project'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(Integer)
    process = Column(String)
    create_at = Column(DateTime, default=datetime.datetime.now())

    @classmethod
    def load_projects(cls):
        db = Session()
        projects = db.query(SpiderProject).filter(SpiderProject.status==1).all()
        return projects

class SpiderTask(Base):
    __tablename__ = 'spider_task'
    id = Column(Integer, primary_key=True)
    project = Column(String)
    task_id = Column(String)
    url = Column(String)
    process = Column(String)
    priority = Column(Integer)
    #next_time = Column(Integer)
    last_time = Column(Integer)
    status = Column(Integer)
    result = Column(String)
    create_at = Column(DateTime, default=datetime.datetime.now())

    @classmethod
    def load_tasks(cls, project):
        #tasks = SchedulerTask.query.filter(SchedulerTask.project==project, SchedulerTask.status==0).order_by('priority').limit(30).all()
        tasks = SchedulerTask.query.filter_by(project=project, status=0).order_by('priority').limit(30).all()
        
        db = Session()
        new_tasks = []
        for task in tasks:
            task.status = 1
            db.add(task)
            new_task={}
            new_task['id'] = task.id
            new_task['task_id'] = task.task_id
            new_task['project'] = task.project
            new_task['url'] = task.url
            new_task['process'] = task.process
            new_tasks.append(new_task)
        db.commit()
        db.close()
        return new_tasks
Task = SpiderTask


class SpiderScheduler(Base, BaseMixin):
    __tablename__ = 'spider_scheduler'
    id = Column(Integer, primary_key=True)
    project = Column(String)
    task_id = Column(String) #data://project/on_start
    url = Column(String) # data://on_start   http://
    process = Column(String) #{callback: '', 'crontab'}
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


