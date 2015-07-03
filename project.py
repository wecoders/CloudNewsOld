import sys
import redis
import json


host='localhost'
port=6379
db=0

op = sys.argv[1]
project_name=sys.argv[2]

redis = redis.StrictRedis(host=host, port=port, db=db)
start_command = {'op':op, 'target':'project', 'target_id':project_name}  

redis.rpush('command_q', json.dumps(start_command))
