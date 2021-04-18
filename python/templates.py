import datetime
import pathlib

import jinja2

from mc_version import MCVer


@jinja2.contextfunction
def show_classifier(context, mc_version, classifier):
    filters = context.parent['filters']
    mc_vers = MCVer(mc_version)
    filter = next(reversed([f['filter'] for f in filters if mc_vers >= f['mc']]), [])
    return classifier not in filter


def humanformatdate(dt: datetime.datetime):
    now = datetime.datetime.now()
    delta = dt - now
    days = abs(delta.days)
    years = days // 365
    days = days % 365
    months = int(days // 30.5)

    if years > 1:
        return f'{years} years ago'
    elif years == 1:
        return f'{months+12} months ago'
    else:
        if days < 2:
            return 'today'
        elif days < 3:
            return 'yesterday'
        elif days < 31:
            return f'{days} days ago'
        elif months < 2:
            return 'a month ago'
        else:
            return f'{months} months ago'


class Templates:
    def __init__(self, template_path: pathlib.Path, static_base, web_base, repository_base):
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
        self.env.globals['static_root'] = static_base
        self.env.globals['web_base'] = web_base
        self.env.globals['repository_base'] = repository_base
        self.env.globals['now'] = datetime.datetime.utcnow()
        self.env.globals['show_classifier'] = show_classifier

        self.env.filters['humanformatdate'] = humanformatdate
        self.env.filters['formatdate'] = lambda dt: f'{dt:%Y-%m-%d %H:%M:%S}'

