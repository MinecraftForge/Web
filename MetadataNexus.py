import os
import json

from http.client import HTTPSConnection
from base64 import b64encode
from pprint import pprint
from datetime import datetime
from Metadata import processVersion, loadConfigDefaults

import Util as Util

def connect(url):
    if url[-1] == '/':
        url = url[:-1]
    if url.lower().startswith('https://'):
        return HTTPSConnection(url[8:])
    elif url.lower().startswith('http://'):
        return HTTPSConnection(url[7:])
    else:
        return HTTPSConnection(url)
    
# /service/rest/v1/script/listClassifiers/run
def postJson(site, path, auth, data):
    c = connect(site)
    headers = { 
        'Authorization' : 'Basic %s' % b64encode(auth.encode('utf-8')).decode('ascii'),
        'Content-type': 'application/json'
    }
    
    c.request('POST', path, json.dumps(data).encode('utf-8'), headers=headers)
    
    res = c.getresponse()
    if res.status != 200:
        return None
    return json.loads(json.loads(res.read())['result']) # Nexus wraps all our reply in a json header, so drill to OUR json

def loadVersions(cache):
    data = Util.readFile(os.path.join(cache, 'versions.json'))
    if data is None:
        return None
    return json.loads(data)

def updateVersionsWeb(url, auth, repo, group, name, cache):
    obj = {'repo': repo, 'group': group, 'name': name}
    data = postJson(url, '/service/rest/v1/script/listVersions/run', auth, obj)
    if not data is None:
        Util.writeFile(os.path.join(cache, 'versions.json'), json.dumps(data, sort_keys=True, indent=2).encode('utf-8'))
    return data

def gatherMetadata(url, auth, repo, group, name, version, cache):
    root = os.path.join(cache, group.replace('.', '/'), name)
    versions = loadVersions(root)
    if versions is None or not 'versions' in versions or (not version is None and not version in versions['versions']):
        versions = updateVersionsWeb(url, auth, repo, group, name, root)
        #TODO: add to the version list without pulling full list?
        
    if versions is None:
        raise Exception('Failed to download version list from %s for %s:%s on %s' % (url, group, name, repo))
        
    #TODO: Add spec verification
        
    metadata = {
        'group'    : group,
        'artifact' : name,
        'name'     : name,
        'mcversion': {},
        'versions' : []
    }
        
    for ver,time in versions['versions'].items():
        vfile = os.path.join(root, 'versions', ver + '.json')
        tfile = os.path.join(root, 'versions', ver + '.json.time')
        
        vdata = None
        if ver == version or not os.path.exists(vfile) or not os.path.exists(tfile) or Util.getFirstFileLine(tfile) != time:
            obj = {'repo': repo, 'group': group, 'name': name, 'version': ver}
            vdata = postJson(url, '/service/rest/v1/script/listClassifiers/run', auth, obj)
            if vdata is None and (os.path.exists(vfile) or os.path.exists(tfile)):
                print('  Removed %s' % ver)
                if os.path.exists(vfile):
                    os.remove(vfile)
                if os.path.exists(tfile):
                    os.remove(tfile)
            elif not vdata is None:
                Util.writeFile(vfile, json.dumps(vdata, sort_keys=True, indent=2).encode('utf-8'))
                Util.writeFile(tfile, time.encode('utf-8'))
        else:
            with open(vfile, 'r') as f:
                vdata = json.loads(f.read())
        
        if vdata is None:
            continue
            
        vdata = convertVersion(metadata, vdata)
        
        if not vdata is None:
            mcver = None
            if 'mcversion' in vdata: mcver = vdata['mcversion']
            if mcver is None: mcver = 'default'
            
            if len(vdata['classifiers']) > 0:
                if not mcver in metadata['mcversion']:
                    metadata['mcversion'][mcver] = []
                metadata['mcversion'][mcver].append(vdata)
                metadata['versions'].append(vdata)
        
    
    blacklist = loadConfigDefaults(metadata)
    #loadConfigFromDirectory(pathRoot, metadata, blacklist)
        
    return metadata
    
def convertVersion(metadata, vdata):
    #TODO: Add spec verification

    ret = {
        'version'     : vdata['version'],
        'version_raw' : vdata['version'],
        'classifiers' : {}
    }
    ver_info = processVersion(metadata, vdata['version'])
    if not ver_info is None:
        ret['version'] = ver_info['version']
        for data in ['mcversion', 'branch', 'forge']:
            if data in ver_info and not ver_info[data] is None:
                ret[data] = ver_info[data]
                
    timestamp = None
    for cls,map in vdata['classifiers'].items():
        for ext,info in map.items():
            mod = datetime.strptime(info['modified'], '%m/%d/%y %I:%M:%S %p')
            if timestamp is None or mod < timestamp:
                timestamp = mod
                
            if cls in ret['classifiers']:
                cls = '%s-%s' % (cls, ext)
                
            ret['classifiers'][cls] = {
                'ext': ext,
                'md5': info['md5'],
                'sha1': info['sha1'],
                'url': vdata['url'] + info['name']
            }
    
    ret['timestamp'] = '01/01/1990 12:00 AM' if timestamp is None else timestamp.strftime('%m/%d/%y %I:%M %p')
                
    return ret
    