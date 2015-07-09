import sys
import redis
import json

from easyspider.db import SpiderProject, ScopedSession
host='localhost'
port=6379
db=0

op = sys.argv[1]
project_name=sys.argv[2]

redis = redis.StrictRedis(host=host, port=port, db=db)
start_command = {'op':op, 'type':'project', 'target':project_name}  

redis.rpush('command_q', json.dumps(start_command))

project = SpiderProject.query.filter_by(name=project_name).first()
if op == 'start' or op == 'reload':
    project.status = 1
elif op == 'stop':
    project.status = 0

db = ScopedSession()
db.add(project)
db.commit()
