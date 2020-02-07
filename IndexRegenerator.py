import os
import datetime
import re
import json
import hashlib
import sys

import subprocess as sp
import xml.etree.ElementTree as ET
import Util as Util
import Promote as Promote

from pprint import pprint
from markdown import markdown
from jinja2 import Template
from copy import deepcopy
from time import time, ctime
from MCVer import MCVer

def read_template(name):
    data = ''
    with open('%s/templates/%s' % (os.path.split(os.path.realpath(__file__))[0], name), 'rb') as f:
        data = f.read().decode('utf-8')
    return data


#page_directory_template = page_header + read_template('page_directory_body.html') + page_footer
#default_template_directory = Template(page_directory_template)

# Page Designed by PaleoCrafter
# http://forge.mineformers.de/
def loadIndexTemplate(static):
    page_header = read_template('page_header.html').replace('{{page_style}}', read_template('page_style.css'))
    page_footer = read_template('page_footer.html')
    return Template((page_header + read_template('page_body.html') + page_footer).replace('{{ static_root }}', static))

def regenerateAtPath(metadata, webRoot, group, name, root, root_meta, root_static):
    root = os.path.join(root, group.replace('.', '/'), name)
    if webRoot[-1] != '/':
        webRoot = webRoot + '/'
    print('Regenerating:')
    print('  Web:    ' + root)
    print('  Meta:   ' + root_meta)
    print('  Static: ' + root_static)
    
    if metadata is None:
        print('  Exiting: No metadata')
        return
    
    if len(metadata['versions']) == 0:
        print('  WARNING:  Artifact has no valid versions: %s' % mavenMetadata)
        return
    
    dumpVersionMeta(metadata, root_meta)
    dumpMavenMetaJson(metadata, root_meta)
    dumpIndexPages(metadata, group, name, root, webRoot, loadIndexTemplate(root_static))
    
    # TODO Generate parent indexes
    #t = time()
    #regenerateDirectoryIndexes(os.path.dirname(root[:-1]), pathBase, False, webRoot)
    #print "    Generated parent templates in {0} seconds".format(time() - t)
    
def dumpVersionMeta(metadata, root):
    #==============================================
    #          meta.json
    #  Maven does not supply a list of classifiers
    # per version. We add it to prevent people 
    # from pinging 404s.
    #
    #  {
    #    "timestamp": "MM/DD/YY HH:MM:SS UTC",
    #    "classifiers": {
    #      "classifier": {
    #        "ext": "md5"
    #      }
    #    }
    #  }
    #==============================================
    t = time()
    for version in metadata['versions']:
        metaPath = os.path.join(root, version['version_raw'], 'meta.json')
        meta = {
            'timestamp': version['timestamp'],
            'classifiers': {}
        }
        
        for cls,info in version['classifiers'].items():
            if not cls in meta['classifiers']:
                meta['classifiers'][cls] = {}
            meta['classifiers'][cls][info['ext']] = info['md5']
        
        index = json.dumps(meta, sort_keys=True, indent=2, separators=(',', ': ')).encode('utf-8')
        Util.writeFileHashed(metaPath, index)
    print('  Generated version metas in %1.2f seconds' % (time() - t))

def dumpMavenMetaJson(metadata, root):
    #==============================================
    #          maven-metadata.json
    #  Json format of maven-metadata to list all
    # versions. We also split by minecraft version
    # for ease of consumption. 'default' is used for
    # versions that have no associated MC Version
    #
    #  {
    #    "mc_version": [
    #      "full_version"
    #    ]
    #  }
    #==============================================
    t = time()
    index_json = {}
    for version in metadata['versions']: # Done before index so we can access versions correctly.
        mcver = 'default'
        if 'mcversion' in version:
            mcver = version['mcversion']
        if not mcver in index_json:
            index_json[mcver] = []
        index_json[mcver].append(version['version'])
        
    for ver in index_json:
        index_json[ver] = sorted(index_json[ver], reverse=False)
        
    Util.writeFileHashed(os.path.join(root, 'maven-metadata.json'), json.dumps(index_json, sort_keys=True, indent=2, separators=(',', ': ')).encode('utf-8'))
    print('  Generated maven meta in %1.2f seconds' % (time() - t))
    
def dumpIndexPages(metadata, group, name, root, webRoot, template):
    t = time()
    webPath = webRoot + group.replace('.', '/') + '/' + name + '/'

    description = ''
    if 'description' in metadata and not metadata['description'] is None:
        description = markdown(metadata['description'].join('\n'))
    
    filters = []
    if 'filters' in metadata:
        for mc in sorted(metadata['filters'], key=lambda a: MCVer(a)):
            filters.append({
                'mc': MCVer(mc),
                'filter': metadata['filters'][mc]
            })
            
    def getFilters(version):
        ret = None
        mver = MCVer(version)
        for f in filters:
            if f['mc'] <= MCVer(version):
                ret = f['filter']
        return [] if ret is None else ret
    
    def filterVersions(versions, filter=None):
        ret = versions
        for version in ret:
            if filter is None:
                if 'mcversion' in version:
                    version['classifiers'] = {key: value for key, value in version['classifiers'].items() if not key in getFilters(version['mcversion'])}
            else:
                version['classifiers'] = {key: value for key, value in version['classifiers'].items() if not key in filter}
        return ret
    
    if 'splitpages' in metadata and metadata['splitpages'] == True:
        sorted_versions = sorted(metadata['mcversion'].keys(), reverse=True, key=lambda a: MCVer(a))

        for version in sorted_versions:
            metadata['versions'] = filterVersions(metadata['mcversion'][version], filter=getFilters(version))
            metadata['mcver'] = version
            data = template.render(md=metadata, name=metadata['name'], description=description, path=webPath, mcversions=sorted_versions, time_now_seconds=t)
            Util.writeFile(os.path.join(root, 'index_%s.html' % version), data.encode('utf-8'))

        index_ver = None
        if 'promos' in metadata:
            for version in sorted_versions:
                if version in metadata['promos'] and 'RECOMMENDED' in metadata['promos'][version]:
                    index_ver = version
                    break

        if index_ver is None:
            index_ver = sorted_versions[0]

        metadata['versions'] = filterVersions(metadata['mcversion'][index_ver], filter=getFilters(index_ver))
        metadata['mcver'] = index_ver
        data = template.render(md=metadata, name=metadata['name'], description=description, path=webPath, mcversions=sorted_versions, time_now_seconds=t)
        Util.writeFile(os.path.join(root, 'index.html'), data.encode('utf-8'))
    else:
        metadata['versions'] = filterVersions(metadata['versions'])
        data = template.render(md=metadata, name=metadata['name'], description=description, path=webPath,  time_now_seconds=t)
        Util.writeFile(os.path.join(root, 'index.html'), data.encode('utf-8'))
    
    print('  Generated index pages in %1.2f seconds' % (time() - t))

def regenerateDirectoryIndexes(pathRoot, pathBase, showChildren=False, webroot=None):
    if not pathBase.endswith('/'): pathBase += '/'
    if not pathRoot.endswith('/'): pathRoot += '/'
    if not pathRoot.startswith(pathBase): return
    
    #print 'Root:  %s' % pathRoot
    #print 'Baase: %s' % pathBase
    #print 'Web:   %s' % webroot
    
    paths = []
    for f in os.listdir(pathRoot):
        fullPath = pathRoot+f
        
        if not os.path.isdir(fullPath): continue
        if not os.path.isfile(os.path.join(fullPath, 'index.html')): continue
        if f == 'manage': continue
        
        children = []
        for c in os.listdir(fullPath):
            child = os.path.join(fullPath, c)
            if showChildren and os.path.isdir(child) and os.path.isfile(os.path.join(child, 'index.html')):
                children.append(c)
        
        paths.append({
            'path':f,
            'path_full': webroot + '/' + fullPath[len(pathBase):] +'/',
            'timestamp':ctime(os.path.getmtime(fullPath)),
            'children':children
            })
    
    print('Writing folder index: %s' % pathRoot)
    with open(pathRoot + "index.html", 'w') as f:
        f.write(default_template_directory.render(name=os.path.basename(pathRoot[:-1]), paths=paths, md={}, custom_style=None, time_now_seconds=time(), webroot=webroot))
    
    regenerateDirectoryIndexes(os.path.dirname(pathRoot[:-1]), pathBase, True, webroot)
    