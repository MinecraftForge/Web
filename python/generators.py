import argparse
import json
import time
from abc import abstractmethod
from collections import ChainMap

from markdown import markdown

import metadata
import templates
from mc_version import MCVer


class Generator:
    @abstractmethod
    def generate(self, md: metadata.Metadata, artifact: metadata.Artifact, tpl: templates.Templates, args: argparse.Namespace):
        pass


class MetaJsonGenerator(Generator):
    def generate(self, md: metadata.Metadata, artifact: metadata.Artifact, tpl: templates.Templates, args: argparse.Namespace):
        for version in artifact.all_versions:
            meta = {'classifiers': {cls or "null": {item.ext: item.md5} for cls, item in version.item_by_cls.items()}}
            out = version.path(root='output_meta')
            print(f'Writing meta.json at {out}')
            out.mkdir(parents=True, exist_ok=True)
            out.joinpath('meta.json').write_text(json.dumps(meta, indent=2), 'utf-8')


class MavenJsonGenerator(Generator):
    def generate(self, md: metadata.Metadata, artifact: metadata.Artifact, tpl: templates.Templates, args: argparse.Namespace):
        meta = {mc_vers: list(vers.keys()) for mc_vers, vers in artifact.versions.items()}
        out = artifact.path(root='output_meta')
        print(f'Writing maven_metadata.json at {out}')
        out.mkdir(parents=True, exist_ok=True)
        out.joinpath('maven-metadata.json').write_text(json.dumps(meta, indent=2), 'utf-8')


class IndexGenerator(Generator):
    def generate(self, md: metadata.Metadata, artifact: metadata.Artifact, tpl: templates.Templates, args: argparse.Namespace):
        description = markdown('\n'.join(artifact.config.get('description', [])))

        config_filters = artifact.config.get('filters', {})
        filter_list = [{'mc': MCVer(mc_ver), 'filter': config_filters[mc_ver]} for mc_ver in sorted(config_filters, key=lambda v: MCVer(v))]
        out = artifact.path(root='output_web')
        out.mkdir(parents=True, exist_ok=True)
        print(f'Writing index files at {out}')
        render_context = {'md': md, 'artifact': artifact, 'description': description, 'filters': filter_list}
        template = tpl.env.get_template('base_page.html')
        for (file, context) in artifact.parts(render_context):
            out.joinpath(file).write_text(template.render(**context), 'utf-8')


class PromoteGenerator(Generator):
    def generate(self, md: metadata.Metadata, artifact: metadata.Artifact, tpl: templates.Templates, args: argparse.Namespace):
        print(f'Promoting {artifact.name} version {args.version} to {args.type}')
        artifact.promote(args.version, args.type)

        slimpromos = {
            "homepage": f'{md.web_root}{artifact.path(root="empty_root")}/',
            "promos": dict(ChainMap(*[{f'{mcv}-{tag.lower()}': v for tag, v in vers.items()} for mcv, vers in artifact.promotions.items()]))
        }

        out = artifact.path(root='output_meta')
        out.mkdir(parents=True, exist_ok=True)
        print(f'Writing promotion files at {out}')
        out.joinpath('promotions_slim.json').write_text(json.dumps(slimpromos, indent=2), 'utf-8')


basegens = [MetaJsonGenerator(), MavenJsonGenerator(), IndexGenerator()]
Generators: dict[str, list[Generator]] = {
    'gen': basegens,
    'promote': [PromoteGenerator(), *basegens]
}
