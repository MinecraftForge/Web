import datetime
import itertools
import pathlib
import re
import requests
import zlib

import jinja2
import markupsafe

from mc_version import MCVer
from metadata import Artifact

@jinja2.pass_context 
def show_classifier(context, mc_version, classifier):
    filters = context.parent['filters']
    mc_vers = MCVer(mc_version)
    filter = next(reversed([f['filter'] for f in filters if mc_vers >= f['mc']]), [])
    return classifier not in filter


def humanformatdate(dt: datetime.datetime):
    return markupsafe.Markup(f'<script>document.write(dayjs.unix({dt.timestamp()}).fromNow())</script>')


def get_artifact_description(artifact: Artifact, mc_version):
    if mc_version:
        hdr = (f'Downloads for {artifact.fullname()} for Minecraft {mc_version}',)
        lines = (f'{t.capitalize()}: {v}' for t, v in artifact.promotions[mc_version].items())
    else:
        hdr = (f'Downloads for {artifact.fullname()}',)
        lines = (f'Latest: {artifact.all_versions[-1].version}',)

    return '\n'.join(itertools.chain(hdr, lines))

def crc32(file_path: str, chunk_size: int = 4096) -> str:
    """Computes the CRC32 checksum of the contents of the file at the given file_path"""
    checksum = 0
    with open('./static/' + file_path, 'rb') as f:
        while (chunk := f.read(chunk_size)):
            checksum = zlib.crc32(chunk, checksum)

    return "%08X" % (checksum & 0xFFFFFFFF)

class Templates:
    def __init__(self, template_path: pathlib.Path, static_base, web_base, repository_base):
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
        self.env.globals['static_root'] = static_base
        self.env.globals['web_base'] = web_base
        self.env.globals['repository_base'] = repository_base
        now = datetime.datetime.utcnow()
        self.env.globals['now'] = now
        self.env.globals['crc32'] = crc32
        self.env.globals['show_classifier'] = show_classifier
        self.env.globals['get_artifact_description'] = get_artifact_description

        self.env.filters['humanformatdate'] = humanformatdate
        self.env.filters['formatdate'] = lambda dt: f'{dt:%Y-%m-%d %H:%M:%S}'
        self.env.filters['formatdatesimple'] = lambda dt: f'{dt:%Y-%m-%d}'
        self.env.filters['todatetime'] = lambda f: datetime.datetime.fromtimestamp(f)
        self.env.filters['maventopath'] = lambda p: '/'.join(re.split(r"[:.]", p))

