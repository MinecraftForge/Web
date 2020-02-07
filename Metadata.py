# Functions used to gather metadata about a maven artifact.
# Each returns meta in the following structure:
#
#
#
#{
#  'artifact': 'forge',
#  'group': 'net.minecraftforge',
#  'name': 'forge',
#  'versions':
#    [
#      {
#        'classifiers':
#        {
#          'ext': 'txt',
#          'path': 'https://files.minecraftforge.net/maven/net/minecraftforge/forge/1.1-1.3.2.1/forge-1.1-1.3.2.1-changelog.txt',
#          'sha1': '54cad7061be90552e15f0a742dbae6f52426d1ff',
#          'md5': '84eb0d8c5574ebd10d8c8b71e519b61f'
#        },
#        'timestamp': 'Sat Nov 15 19:46:59 2014',
#        'version': '0.1.0',
#        'version_raw': '1.1-1.3.2.1',
#        'mcversion': '1.1', # Optional, missing if not parseable into mc versions
#        'branch': 'bugfixes', # Optional, missing if not in a branch
#        'forge': '1.3.2.1' # Optional, used by Sponge to link 'recomnded' forge versions
#      }
#    ],
#  'mcversion': # Optional, if artifact isn't parseable into MC version
#    {
#      'mcversion': [array of objects like in versions]
#    }
#  'promos' :
#    {
#      'PromoName' : 'Version'
#    }
#}

import os
from time import time, ctime, strftime, localtime
import xml.etree.ElementTree as ET
from pprint import pprint
from glob import glob
import re
import json

import Util as Util
import Promote as Promote

# Generic format, 1.0.0-BRANCH unlimited number of digit parts
BASIC_REG = re.compile(r'^(?P<version>(?:\d+\.)*[\d]+)-?(?P<branch>[\w\.\-]+)?$')
#1.8-1521-2.1-DEV-729
SPONGEFORGE_REG = re.compile(r'^(?P<forge>\d+)-(?P<version>(?:(?:\d+\.?)+)?-(?:[\w\.]+)-(?:\d+))-?(?P<branch>[\w\.\-]+)?$')
SPONGEFORGE_REG_NEW = re.compile(r'^(?P<forge>(?:\d+))-(?P<version>[\d.]+(?:-RC(?:\d+))?)$')

#Weekly snapshots are only ever in ##w##a 18w10a
SNAPSHOT_REG = re.compile(r'^(?:\d\d)w(?:\d\d)(?:[a-z])$')
#1.12.1_pre4 Must start with 1, I can change this if MC ever releases a 2.0. Must have between 1 and 2 additional number sets. And if it is a pre, must be named _pre not -pre. This is to simplify the splitting at the beginning
MINECRAFT_REG = re.compile(r'^(?P<mcversion>1(?:\.\d+){1,2}?(?:_pre\d+)?)$')

#Values used:
# mcversion, version, branch, forge
#TODO: Loosen up restrictions and go full https://maven.apache.org/ref/3.3.3/maven-artifact/apidocs/org/apache/maven/artifact/versioning/ComparableVersion.html ?
def processVersion(metadata, version):
    artifact = metadata['group'] + ':' + metadata['artifact']
    ret = None
    mcver = None
    if '-' in version:
        mc, extra = version.split('-', 1)
        if validMCVersion(mc):
            mcver = mc
            version = extra
            
    if artifact == 'org.spongepowered:spongeforge':
        match = SPONGEFORGE_REG_NEW.match(version)
        if not match is None:
            ret = match.groupdict()
        match = SPONGEFORGE_REG.match(version)
        if ret is None and not match is None:
            ret = match.groupdict()
    else:
        match = BASIC_REG.match(version)
        if not match is None:
            ret = match.groupdict()
    
    if ret is None and not mcver is None:
        version = '%s-%s' % (mcver, version)
        mcver = None
        match = BASIC_REG.match(version)
        if not match is None:
            ret = match.groupdict()
    
    if not ret is None and not mcver is None:
        ret['mcversion'] = mcver
    
    return ret

def validMCVersion(version):
    if not SNAPSHOT_REG.match(version) is None:
        return True
    return not MINECRAFT_REG.match(version) is None

def gatherMetadataFromDirectory(mavenRoot, group, name, dlroot):
    mavenMetadataXML = os.path.join(mavenRoot, '%s/%s/maven-metadata.xml' % (group.replace('.', '/'), name))
    print('Loading metadata from XML: %s' % mavenMetadataXML)
    pathRoot = os.path.dirname(mavenMetadataXML) + '/'
    try:
        if not os.path.isfile(mavenMetadataXML):
            print('File does not exist: %s' % mavenMetadataXML)
            return None
        if os.path.getsize(mavenMetadataXML) > 1024*1024*8:
            print('File is too huge: %s' % mavenMetadataXML)
            return None
    except OSError as e:
        print('Invalid filepath \'%s\' with error %s: %s' % (mavenMetadataXML, e.errno, e.strerror))
        return None
    
    root = ET.parse(mavenMetadataXML).getroot()
    
    #version_tag = root.find('./version').text if root.find('./version') else ''
    #group = root.find('./groupId').text
    #artifact = root.find('./artifactId').text
    versions = [v.text for v in root.findall("./versioning/versions/version")]
    
    return buildMetadataFromDirectory(pathRoot, mavenRoot, group, name, versions, dlroot)

def buildMetadataFromDirectory(pathRoot, mavenRoot, group, name, versions, dlroot):
    if dlroot[-1] != '/':
        dlroot = dlroot + '/'
        
    print('Building Metadata: ')
    print('    Root:     ' + pathRoot)
    print('    Maven:    ' + mavenRoot)
    print('    Group:    ' + group)
    print('    Artifact: ' + name)
    print('    DLRoot:   ' + dlroot)
    #print('    Versions: ' + ', '.join(versions))
    
    metadata = {
        'group'    : group,
        'artifact' : name,
        'name'     : name,
        'mcversion': {},
        'versions' : []
        #'path'       : pathRoot.replace(mavenRoot, '').replace('\\', '/'),
        #'logo'       : None, #'logo.png' if os.path.isfile(pathRoot + 'logo.png') else ('logo.jpeg' if os.path.isfile(pathRoot + 'logo.jpeg') else None),
        #'header_bg'  : None, #'header_bg.png' if os.path.isfile(pathRoot + 'header_bg.png') else ('header_bg.jpeg' if os.path.isfile(pathRoot + 'header_bg.jpeg') else None)
    }
    
    #if '_' in metadata['artifact']: # Some Artifacts have the MC version in their name.
    #    nameParts = metadata['artifact'].rsplit('_', 1)
    #    if (validMCVersion(nameParts[1])):
    #        metadata['name'] = nameParts[0]
    #        metadata['mcver'] = nameParts[1]
    
    for v in versions:
        verdlroot = dlroot + group.replace('.', '/') + '/' + name + '/' + v + '/'
        version = buildVersionFromDirectory(pathRoot, v, metadata, verdlroot)
        if not version is None:
            mcver = None
            if 'mcversion' in version: mcver = version['mcversion']
            if mcver is None: mcver = 'default'
            
            if len(version['classifiers']) > 0:
                if not mcver in metadata['mcversion']:
                    metadata['mcversion'][mcver] = []
                metadata['mcversion'][mcver].append(version)
                metadata['versions'].append(version)
    
            
    #attachPromotions(metadata, output, group, name)
    blacklist = loadConfigDefaults(metadata)
    loadConfigFromDirectory(pathRoot, metadata, blacklist)
    return metadata

def buildVersionFromDirectory(pathRoot, version, metadata, dlroot):
    verpathRoot = os.path.normpath(pathRoot + version) + '/'
    if not os.path.isdir(verpathRoot):
        print('  Version path is not valid: %s' % verpathRoot)
        return None
    
    ret = {
        'version'     : version,
        'version_raw' : version,
        'timestamp'   : strftime('%m/%d/%y %I:%M %p', localtime(os.path.getmtime(verpathRoot))),
        'classifiers' : {}
    }
    ver_info = processVersion(metadata, version)
    if not ver_info is None:
        ret['version'] = ver_info['version']
        for data in ['mcversion', 'branch', 'forge']:
            if data in ver_info and not ver_info[data] is None:
                ret[data] = ver_info[data]
    
    timestamp = None
    fileverstart = '%s-%s' % (metadata['artifact'], version)
    for f in os.listdir(verpathRoot):
        filepath = verpathRoot + f
        if not '.' in f:
            print('  Invalid filename: %s' % filepath)
            continue
        name, ext = f.rsplit('.', 1)
        if os.path.isdir(filepath) or not name.startswith(fileverstart): #TODO: Support listing SNAPSHOTs?
            continue
            
        if ext in ['pom', 'sha1', 'md5', 'url', 'asc']:
            continue
            
        if (timestamp is None):
            timestamp = strftime('%m/%d/%y %I:%M %p', localtime(os.path.getmtime(filepath)))
            ret['timestamp'] = timestamp
            
        subpath = '%s/%s' % (version, f)
        classifier = None if len(name) <= len(fileverstart) else name[len(fileverstart) + 1:]
        if not classifier in ret['classifiers']:
            ret['classifiers'][classifier] = {}
            
        ret['classifiers'][classifier] = {
            'url': dlroot + f,
            'ext': ext,
            'md5': Util.getFirstFileLine(filepath + '.md5'),
            'sha1': Util.getFirstFileLine(filepath + '.sha1')
        }
    
    return ret

def attachPromotions(metadata, root, group, name):
    data = Promote.loadPromotions(root, group.replace('.', '/'), name)
    if 'promos' in data:
        metadata['promos'] = {}
        for key,value in data['promos'].items():
            if key.count('-') == 1:
                pts = key.split('-')
                if not pts[0] in metadata['promos']:
                    metadata['promos'][pts[0]] = {}
                metadata['promos'][pts[0]][pts[1].upper()] = value
                if pts[0] in metadata['mcversion']:
                    for version in metadata['mcversion'][pts[0]]:
                        if version['version'] == value:
                            version['marker'] = pts[1].upper()

def loadConfigDefaults(metadata):
    for key in metadata['mcversion']:
        metadata['mcversion'][key] = sorted(metadata['mcversion'][key], key=lambda e: e['version'])
    metadata['versions'] = sorted(metadata['versions'], key=lambda e: e['version'])
    metadata['splitpages'] = len([v for v in metadata['mcversion'] if not v == 'Default']) > 0
    
    blacklist = []
    dfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'global_overrides.json')
    if os.path.isfile(dfile):
        overrides = json.loads(open(dfile).read())
        for key,value in overrides.items():
            metadata[key] = value
            blacklist.append(key)
            
    return blacklist

def loadConfigFromDirectory(root, metadata, blacklist):
    cfile = os.path.join(root, 'page_config.json')
    if os.path.isfile(cfile):
        config = json.loads(open(cfile).read())
        for key,value in config.items():
            if not key in blacklist:
                metadata[key] = value