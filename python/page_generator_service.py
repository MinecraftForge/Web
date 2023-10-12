import waitress
import logging
import os
import time
import json
import base64
from threading import Thread
from enum import Enum
from flask import Flask, request
from queue import PriorityQueue
from pprint import pprint
from paste.translogger import TransLogger

import page_generator

logging.basicConfig(level = logging.NOTSET)
logging.getLogger('waitress').setLevel(logging.INFO)

logger = logging.getLogger('pagegen')
logger.setLevel(logging.DEBUG)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 # Posts should never need more then 1KB

tasks = PriorityQueue()
users = {}
config = {}

TaskTypes = Enum('TaskTypes', ['PROMOTE', 'REGEN_INDEX', 'GEN', 'REGEN'])
    
class Task:
    def __init__(self, type, data):
        self.type = type
        self.data = data
        
    def __repr__(self):
        return "Task(type={}, data={})".format(self.type, self.data)
        
    def __gt__(self, other):
        return self.type.value > other.type.value
    def __lt__(self, other):
        return self.type.value < other.type.value
    def __eq__(self, other):
        return self.type.value == other.type.value

@app.route('/promote', methods = ['POST'])
@app.route('/promote/<type>/<path:group>/<artifact>/<version>', methods = ['GET'])
def promote(type=None, group=None, artifact=None, version=None):
    data = {}
    if request.method == 'GET':
        data = {
            'type': type,
            'group': group.replace('/', '.'),
            'artifact': artifact,
            'version': version
        }
    elif request.method == 'POST':
        data = request.get_json()
    else:
        return 'Unsupported Request', 404
    
    if data.get('type') == None or data.get('group') == None or data.get('artifact') == None or data.get('version') == None:
        return "Missing promotion target: {}".format(data), 400
        
    if not data['type'] in ['latest', 'recommended']:
        return "Invalid promotion type {} only latest or recommended supported".format(data["type"]), 400
    
    loginResponse = checkAccess(data)
    if loginResponse:
        return loginResponse
        
    logger.info("Queueing Promotion: {}:{}:{} {}".format(data['group'], data['artifact'], data['version'], data['type']))
    tasks.put(Task(TaskTypes.PROMOTE, data))
    
    return 'Promotion Queued'

@app.route('/gen', methods = ['POST'])
@app.route('/gen/<path:group>/<artifact>', methods = ['GET'])
def gen(group=None, artifact=None):
    data = {}
    if request.method == 'GET':
        data = {
            'group': group.replace('/', '.'),
            'artifact': artifact
        }
    elif request.method == 'POST':
        data = request.get_json()
    else:
        return 'Unsupported Request', 404
        
    if data.get('group') == None or data.get('artifact') == None:
        return "Missing generator target: {}".format(data), 400
    
    loginResponse = checkAccess(data)
    if loginResponse:
        return loginResponse
        
    logger.info("Queueing Gen: {}:{}".format(data['group'], data['artifact']))
    tasks.put(Task(TaskTypes.GEN, data))
    
    return 'Generation Queued'
    
@app.route('/regen', methods = ['GET'])
def regen():
    loginResponse = checkAccess({'group': '', 'artifact': ''})
    if loginResponse:
        return loginResponse
        
    logger.info("Queueing Complete Regen")
    tasks.put(Task(TaskTypes.REGEN, {}))
    
    return 'Complete Generation Queued'
    
@app.route('/regen-index', methods = ['GET'])
def regen_index():
    loginResponse = checkAccess({'group': '', 'artifact': ''})
    if loginResponse:
        return loginResponse
        
    logger.info("Queueing Index Regen")
    tasks.put(Task(TaskTypes.REGEN_INDEX, {}))
    
    return 'Index Generation Queued'
    
def process_queue():
    while tasks:
        task = tasks.get()
        logger.info(task)
        data = task.data
        key = task.type.name.lower()
        args = []
        if key in config and 'args' in config[key]:
            args += config[key]['args']
        
        if task.type == TaskTypes.PROMOTE:
            logger.info('Promoting %s:%s', data['group'], data['artifact'])
            args += ['promote', data['group'] + ':' + data['artifact'], data['version'], data['type']]
        elif task.type == TaskTypes.REGEN:
            logger.info('Regnerating Everything')
            args += ['regen']
        elif task.type == TaskTypes.REGEN_INDEX:
            logger.info('Regnerating Tracked Index')
            args += ['index']
        elif task.type == TaskTypes.GEN:
            logger.info('Generating %s:%s', data['group'], data['artifact'])
            args += ['gen', data['group'] + ':' + data['artifact']]
            
        try:
            page_generator.main(args)
        except Exception as e:
            logger.error('Failed to run generator: %s', e)
            
    logger.error("Task queue ended")
        
def load_users():
    global users
    logger.info('Loading users...')
    if not os.path.isfile('/config/users.json'):
        raise 'Missing /config/users.json, No authentication will work'
        
    with open('/config/users.json', 'r') as f:
        users = json.load(f)
    
    logger.info("Loaded %d users", len(users))

def load_config():
    global config
    logger.info('Loading config...')
    if not os.path.isfile('/config/config.json'):
        logger.warning('Missing /config/config.json, Its non critical for now')
        return
        
    with open('/config/config.json', 'r') as f:
        config = json.load(f)
    
    logger.info('Loaded config file')
    
def checkAccess(data):
    global users
    
    if not 'Authorization' in request.headers:
        logger.info('Ignoring anonymous user')
        return '', 401, {'WWW-Authenticate': 'BASIC realm="Forge Maven"'}
        
    auth = request.headers.get('Authorization')
    
    if (auth.startswith('Basic ')):
        try:
            auth = base64.b64decode(auth[6:]).decode('utf-8')
        except TypeError:
            return 'Failed to decode base auth', 401, {'WWW-Authenticate': 'BASIC realm="Forge Maven"'}
    
    user,password = auth.split(':', 1)
    if not user in users:
        logger.info("Unknown user: %s", user)
        return 'Unauthorized', 401, {'WWW-Authenticate': 'BASIC realm="Forge Maven"'}
    
    if not users[user]['password'] == password:
        logger.info('User %s failed to login, invalid password', user)
        return 'Unauthorized', 401, {'WWW-Authenticate': 'BASIC realm="Forge Maven"'}
    
    success = False
    for access in users[user]['access']:
        if access['group'] == data['group'] or access['group'] == '':
            if access['artifact'] == data['artifact'] or access['artifact'] == '':
                success = True
                break
    
    if not success:
        logger.info('User %s does not have access to %s:%s', user, data['group'], data['artifact'])
        return 'Unauthorized', 401, {'WWW-Authenticate': 'BASIC realm="Forge Maven"'}
    
    logger.info('User %s permitted to access %s:%s', user, data['group'], data['artifact'])
    return None

if __name__ == "__main__":
    load_config()
    load_users()
    
    processor = Thread(target=process_queue)
    processor.start()
    #app = TransLogger(app, setup_console_handler=False)
    waitress.serve(app, host='0.0.0.0', port=5000)