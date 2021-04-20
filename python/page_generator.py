import argparse
import pathlib
import sys

from metadata import Metadata, Artifact
from templates import Templates
from generators import Generators

def parse_path(f):
    if (p := pathlib.Path(f).absolute()).exists():
        return p
    else:
        raise ValueError('The path is missing')

def main():
    parser = argparse.ArgumentParser(description='Maven based download index generator')
    parser.add_argument('--webout', dest='output_web', default='/out', help='Base directory to output generated index pages. Will generate in sub-directories based on the maven path', type=parse_path)
    parser.add_argument('--metaout', dest='output_meta', default='/out', help='Base directory to output generated metadata. Will generate in sub-directories based on the maven path', type=parse_path)
    parser.add_argument('--downloadroot', dest='dlroot', default='https://maven.minecraftforge.net/', help='Root URL for downloading artifacts')
    parser.add_argument('--webroot', dest='webroot', default='https://files.minecraftforge.net', help='Root URL for artifact pages')
    parser.add_argument('--static', dest='static', default='https://files.minecraftforge.net/static/', help='Root URL for static assets used by the templates')

    parser.add_argument('--folder', dest='folder', default='/in/repositories/releases/', help='Root directory for the maven structure to read metadata from files', type=parse_path)
    parser.add_argument('--config', dest='config', default='/in/global_overrides.json', help="Location of global_overrides.json file", type=parse_path)
    parser.add_argument('--templates', dest='templates', default='templates', type=parse_path, help="Path to templates")

    commands = parser.add_subparsers(help='Command to perform', dest='command', required=True)

    gen_command = commands.add_parser('gen', help='Indexes generator subcommand')
    gen_command.add_argument('artifact', help='Maven Artifact - net.minecraftforge:forge')

    index_command = commands.add_parser('index', help='Generate tracked project index')

    promote_command = commands.add_parser('promote', help='Promote subcommand')
    promote_command.add_argument('artifact',  help='Maven Artifact - net.minecraftforge:forge')
    promote_command.add_argument('version', help='Maven Version')
    promote_command.add_argument('type', choices=['latest', 'recommended'], help='Type of promotion')
    args = parser.parse_args()

    print('Page Generator:')
    print(f'PyVer:    {sys.version}')
    print(f'Folder:   {args.folder}')
    print(f'Config:   {args.config}')
    print(f'Web Out:  {args.output_web}')
    print(f'Meta Out: {args.output_meta}')
    print(f'WebRoot:  {args.webroot}')
    print(f'DLRoot:   {args.dlroot}')
    print(f'Static:   {args.static}')
    print(f'Templates:{args.templates}')
    print(f'Command:  {args.command}')
    print(f'Artifact: {args.artifact if "artifact" in args else None}')
    print(f'Version:  {args.version if "version" in args else None}')
    print(f'Type:     {args.type if "type" in args else None}')

    metadata = Metadata(args.folder, args.output_meta, args.output_web, args.webroot, args.dlroot, args.static, args.config)
    artifact = Artifact.load_maven_xml(metadata, args.artifact) if 'artifact' in args else None
    templates = Templates(args.templates, args.static, args.webroot, args.dlroot)

    for gen in Generators[args.command]:
        gen.generate(metadata, artifact, templates, args)


if __name__ == '__main__':
    main()
