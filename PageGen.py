import argparse
import sys
import json
import os

import IndexRegenerator as Gen
import Metadata as MetadataFolder
import MetadataNexus as MetadataNexus
import Promote as Promote
import Util as Util

from pprint import pprint

def main():
    parser = argparse.ArgumentParser(description = 'Maven based download index generator.')
    parser.add_argument('--group', dest = 'group', required = True, help = 'Maven Group')
    parser.add_argument('--name', dest = 'name', required = True, help = 'Maven Artifact Name')
    parser.add_argument('--version', dest = 'version', help = 'Maven Version, Regeneration will use the cached data for all versions except the specified one. Useful for minimizing network traffic on nexus updates.')
    parser.add_argument('--webout', dest = 'output_web', default = 'output_web', help = 'Base directory to output generated index pages. Will generate in sub-directories based on the maven path.')
    parser.add_argument('--metaout', dest = 'output_meta', default = 'output_meta', help = 'Base directory to output generated metadata. Will generate in sub-directories based on the maven path.')
    parser.add_argument('--webroot', dest = 'webroot', default = '/maven/', help = 'Root URL for generated web pages')
    parser.add_argument('--static', dest = 'static', default = 'https://files.minecraftforge.net/maven/manage/static/', help = 'Root of the static assets used by the templates')
    
    parser.add_argument('--folder', dest = 'folder', help = 'Root directory for the maven structure to read metadata from files. Not compatible with --nexus.')
    parser.add_argument('--dlroot', dest = 'dlroot', default = 'https://files.minecraftforge.net/maven/', help = 'Root URL for every download, used with the --folder argument as we can\'t automatically find the root web url')
    
    parser.add_argument('--nexus', dest = 'nexus', help = 'Root nexus url, we will use custom scripts to download nessasary metadata. See https://github.com/MinecraftForge/NexusScripts/ Not compatible with --folder.')
    parser.add_argument('--cache', dest = 'cache', default = 'cache', help = 'Directory to store a cache of the metadata to save downloading it every run for an artifact.')
    parser.add_argument('--auth', dest = 'auth', help = 'Username:Password used for accessing the nexus scripts.')
    parser.add_argument('--repo', dest = 'repo', help = 'The nexus repo to search for artifacts in.')
    
    parser.add_argument('--gen', dest = 'task', action = 'store_const', const = 'gen', help = 'Generate web pages')
    parser.add_argument('--promote', dest = 'promote', help = 'Mark a promotion, specify the type')
    
    args = parser.parse_args()
    
    print('Index Regenerator:')
    print('PyVer:    %s' % sys.version)
    print('Group:    %s' % args.group)
    print('Name:     %s' % args.name)
    print('Version:  %s' % args.version)
    print('Web Out:  %s' % args.output_web)
    print('Meta Out: %s' % args.output_meta)
    print('WebRoot:  %s' % args.webroot)
    print('Static:   %s' % args.static)
    
    meta = None
    if not args.folder is None:
        print('Folder:   %s' % args.folder)
        print('DL Root:  %s' % args.dlroot)
        if args.dlroot is None:
            raise Exception('Missing dlroot argument')
        meta = MetadataFolder.gatherMetadataFromDirectory(args.folder, args.group, args.name, args.dlroot)
    elif not args.nexus is None:
        print('Nexus:    %s' % args.nexus)
        print('Cache:    %s' % args.cache)
        print('Repo:     %s' % args.repo)
        if args.auth is None:
            raise Exception('Missing auth argument')
        if args.repo is None:
            raise Exception('Missing repo argument')
        meta = MetadataNexus.gatherMetadata(args.nexus, args.auth, args.repo, args.group, args.name, args.version, args.cache)
    else:
        print('Unknown root, use --folder <folder> or --nexus <url>')
    
    if meta is None:
        print('Failed to load metadata, exiting')
        raise Exception('Failed to load metadata')
        
    MetadataFolder.attachPromotions(meta, args.output_meta, args.group, args.name)
        
    #Util.writeFileHashed('./meta.json', json.dumps(meta, sort_keys=True, indent=2, separators=(',', ': ')).encode('utf-8'))
    
    if args.task == 'gen':
        Gen.regenerateAtPath(meta, args.webroot, args.group, args.name, args.output_web, args.output_meta, args.static)
    elif not args.promote is None:
        if args.version is None:
            print('You MUST specify --version when using --promote')
        else:
            Promote.promoteAtPath(meta, '/maven', args.output_web, args.group, args.name, args.version, args.promote)
    else:
        print('Unknown Task: %s, Use --gen or --promote' % (args.task))
  
if __name__ == '__main__':
    main()