import os
import json
import time
import hashlib
from pprint import pprint

import Util as Util

def promoteAtPath(metadata, webRoot, root, group, name, target, type): #artifact, promoNum, promoType, mavenPath, webRoot):
    type = type.lower()
    print('Promoting %s:%s:%s to %s at %s' % (group, name, target, type, root))
    
    fullRoot = os.path.join(root, group.replace('.', '/'), name)
    promos = loadPromotions(root, group, name)
    
    if not 'homepage' in promos:
        promos['homepage'] = 'https://files.minecraftforge.net%s/%s/%s' % (webRoot, group.replace('.', '/'), name)
    if not 'promos' in promos:
        promos['promos'] = {}
    
    found = False
    for version in metadata['versions']:
        if version['version'] == target or ('mcversion' in version and ('%s-%s' % (version['mcversion'], version['version'])) == target):
            print('  Found version to promote: %s' % version['version'])
            
            if 'mcversion' in version and version['mcversion']:
                promos['promos']['%s-%s' % (version['mcversion'], type)] = version['version']
                if type in promos['promos']:
                    del promos['promos'][type]
            elif not 'branch' in version or not version['branch']:
                promos['promos'][type] = version['version']
                
            print('  Promoting: ' + version['version'])
            found = True
            break
    
    if not found:
        print('  MISSING PROMOTION VERSION:')
        for version in metadata['versions']:
                print('  \'%s\'' % (version['version']))
        return
        #pprint(metadata['versions'])
    
    dumpPromotionsSlim(metadata, fullRoot, promos)
    dumpPromotions(metadata, fullRoot, promos)
        
def dumpPromotionsSlim(metadata, root, promos):
    #==================================================
    #   promotions_slim.json
    # {
    #   "homepage" : "url",
    #   "promos":
    #   {
    #     "promo-name" : "version"
    #   }
    # }
    #==================================================
    Util.writeFileHashed(os.path.join(root, 'promotions_slim.json'), json.dumps(promos, sort_keys=True, indent=2, separators=(',', ': ')).encode('utf-8'))

def dumpPromotions(metadata, root, promos):
    #==================================================
    #    promotions.json
    # {
    #   "webpath" : "url",
    #   "adfly": "673885",
    #   "name": "Minecraft Forge",
    #   "promos": {
    #    "recommended": {
    #      "branch": null,
    #      "build": 1334,
    #      "files": [
    #         [
    #           "exe",
    #           "installer-win",
    #           "99cb461ed1f1bc66a620ebc12d4f5e2b"
    #         ],
    #       ],
    #       "mcversion": "1.8",
    #       "modified": 1425327260.57904,
    #       "version": "11.14.1.1334"
    #     }
    #   }
    # }
    #==================================================
    data = {
        'webpath' : promos['homepage'],
        'name'    : metadata['name'],
        'promos'  : {}
    }
    
    if 'adfly' in metadata:
        data['adfly'] = metadata['adfly']
    if 'adfocus' in metadata:
        data['adfocus'] = metadata['adfocus']
    
    for key, value in promos['promos'].items():
        for version in metadata['versions']:
            if version['version'] == value:
                info = {
                    'branch'    : None if not 'branch' in version else version['branch'],
                    'build'     : 0 if not 'build' in version else version['build'],
                    'mcversion' : None if not 'mcversion' in version else version['mcversion'],
                    'version'   : version['version'],
                    'modified'  : time.mktime(time.strptime(version['timestamp'], '%m/%d/%y %I:%M %p')),
                    'files'     : []
                }
                for classifier, finfo in version['classifiers'].items():
                    info['files'].append([os.path.splitext(finfo['path'])[1][1:], classifier, finfo['md5']])
                data['promos'][key] = info
                break
    
    #print json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))
    Util.writeFileHashed(os.path.join(root, 'promotions.json'), json.dumps(data, sort_keys=True, indent=2, separators=(',', ': ')).encode('utf-8'))

def loadPromotions(root, group, name):
    data = {}
    path = os.path.join(root, group.replace('.', '/'), name, 'promotions_slim.json')
    if os.path.isfile(path):
        data = json.loads(open(path).read())
    return data
