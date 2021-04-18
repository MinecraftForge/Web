import datetime
import pathlib
import humanize

import jinja2

from mc_version import MCVer


@jinja2.contextfunction
def show_classifier(context, mc_version, classifier):
    filters = context.parent['filters']
    mc_vers = MCVer(mc_version)
    filter = next(reversed([f['filter'] for f in filters if mc_vers >= f['mc']]), [])
    return classifier not in filter


class Templates:
    def __init__(self, template_path: pathlib.Path, static_base, web_base, repository_base):
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
        self.env.globals['static_root'] = static_base
        self.env.globals['web_base'] = web_base
        self.env.globals['repository_base'] = repository_base
        self.env.globals['now'] = datetime.datetime.utcnow()
        self.env.globals['show_classifier'] = show_classifier
        self.env.filters['humanformatdate'] = lambda dt: f'{humanize.naturaltime(dt.date, months=True)}'
        self.env.filters['formatdate'] = lambda dt: f'{dt:%Y-%m-%d %H:%M:%S}'

