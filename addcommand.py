
import redis
import json

host='localhost'
port=6379
db=0


redis = redis.StrictRedis(host=host, port=port, db=db)
start_command = {'op':'start', 'target':'project', 'target_id':'douban'}  
stop_command = {'op':'stop', 'target':'project', 'target_id':'douban'}  

redis.rpush('command_q', json.dumps(start_command))

# redis.rpush('command_q', json.dumps(stop_command))

exit_command = {'op':'exit'}  
    
# redis.rpush('command_q', json.dumps(exit_command))
