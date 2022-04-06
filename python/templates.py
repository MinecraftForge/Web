import datetime
import itertools
import pathlib
import re

import jinja2

from mc_version import MCVer
from metadata import Artifact

@jinja2.contextfunction
def show_classifier(context, mc_version, classifier):
    filters = context.parent['filters']
    mc_vers = MCVer(mc_version)
    filter = next(reversed([f['filter'] for f in filters if mc_vers >= f['mc']]), [])
    return classifier not in filter


def humanformatdate(dt: datetime.datetime):
    return jinja2.Markup(f'<script>document.write(dayjs.unix({dt.timestamp()}).fromNow())</script>')


def get_artifact_description(artifact: Artifact, mc_version):
    if mc_version:
        hdr = (f'Downloads for {artifact.fullname()} for Minecraft {mc_version}',)
        lines = (f'{t.capitalize()}: {v}' for t, v in artifact.promotions[mc_version].items())
    else:
        hdr = (f'Downloads for {artifact.fullname()}',)
        lines = (f'Latest: {artifact.all_versions[-1].version}',)

    return '\n'.join(itertools.chain(hdr, lines))


class Templates:
    def __init__(self, template_path: pathlib.Path, static_base, web_base, repository_base):
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
        self.env.globals['static_root'] = static_base
        self.env.globals['web_base'] = web_base
        self.env.globals['repository_base'] = repository_base
        self.env.globals['now'] = datetime.datetime.utcnow()
        self.env.globals['show_classifier'] = show_classifier
        self.env.globals['get_artifact_description'] = get_artifact_description

        self.env.filters['humanformatdate'] = humanformatdate
        self.env.filters['formatdate'] = lambda dt: f'{dt:%Y-%m-%d %H:%M:%S}'
        self.env.filters['todatetime'] = lambda f: datetime.datetime.fromtimestamp(f)
        self.env.filters['maventopath'] = lambda p: '/'.join(re.split(r"[:.]", p))

