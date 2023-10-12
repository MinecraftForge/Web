import argparse
import json
import hashlib
import gzip
import zlib
import os
from abc import abstractmethod

from markdown import markdown

import metadata
import templates
from mc_version import MCVer

# Writes the specified data as utf8, only if the associated md5 file is out of date
# This prevents small file churn when generating indexes. Namely version specific meta.json
# files will almost never change. So we don't need to rewrite them every run.
# This helps disk io, as well as web IO as the metadata doesn't change and invalidate caches.
def writeHashed(out, name: str, data, gzip: bool = False, print_path: bool = True):
    data_utf8 = data.encode('utf-8')
    md5_expected = hashlib.md5(data_utf8).hexdigest()
    file = out.joinpath(f'{name}.md5')
    md5_actual = None if not file.exists() else file.read_bytes().decode('utf-8')
    if not file.exists() or not md5_expected == md5_actual:
        if print_path:
            print(f'  Writing {name} at {out}')
        else:
            print(f'  Writing {name}')
        out.mkdir(parents=True, exist_ok=True)
        out.joinpath(name).write_bytes(data_utf8)
        file.write_text(md5_expected, 'utf-8')
        if gzip:
            write_gzip(out, name, data_utf8, print_path)


def write_gzip(out, name: str, data, print_path: bool):
    file = out.joinpath(name)
    file_gz = out.joinpath(f'{name}.gz')
    if print_path:
        print(f'  Gzip\'ing {name} at {out}')
    else:
        print(f'  Gzip\'ing {name}')

    with gzip.open(file_gz, 'wb', compresslevel=9) as dst:
        dst.write(data)


class Generator:
    @abstractmethod
    def generate(self, md: metadata.Metadata, artifact: metadata.Artifact, tpl: templates.Templates, args: argparse.Namespace):
        pass


class MetaJsonGenerator(Generator):
    def generate(self, md: metadata.Metadata, artifact: metadata.Artifact, tpl: templates.Templates, args: argparse.Namespace):
        print(f'Writing meta.jsons')
        for version in artifact.all_versions:
            meta = {'classifiers': {cls or "null": {item.ext: item.md5} for cls, item in version.item_by_cls.items()}}
            out = version.path(root='output_meta')
            writeHashed(out, 'meta.json', json.dumps(meta, indent=2), args.gzip, True)


class MavenJsonGenerator(Generator):
    def generate(self, md: metadata.Metadata, artifact: metadata.Artifact, tpl: templates.Templates, args: argparse.Namespace):
        print('Generating Maven Index')
        meta = {mc_vers: [value.raw_version for value in vers.values()] for mc_vers, vers in artifact.versions.items()}
        out = artifact.path(root='output_meta')
        writeHashed(out, 'maven-metadata.json', json.dumps(meta, indent=2), args.gzip)


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
            writeHashed(out, file, template.render(**context), args.gzip, False)


class PromoteGenerator(Generator):
    def generate(self, md: metadata.Metadata, artifact: metadata.Artifact, tpl: templates.Templates, args: argparse.Namespace):
        print(f'Promoting {artifact.name} version {args.version} to {args.type}')
        artifact.promote(args.version, args.type)

        slimpromos = {
            "homepage": f'{md.web_root}{artifact.mvnpath()}/',
            "promos": {}
        }
        for mcv, vers in artifact.promotions.items():
            if mcv == 'default':
                for tag, v in vers.items():
                    slimpromos['promos'][tag] = v.lower()
            else:
                for tag, v in vers.items():
                    slimpromos['promos'][f'{mcv}-{tag}'] = v.lower()

        out = artifact.path(root='output_meta')
        out.mkdir(parents=True, exist_ok=True)
        print(f'Writing promotion files at {out}')
        writeHashed(out, 'promotions_slim', json.dumps(slimpromos, indent=2), args.gzip, False)


class TrackingGenerator(Generator):
    def generate(self, md: metadata.Metadata, artifact: metadata.Artifact, tpl: templates.Templates, args: argparse.Namespace):
        out = md.path(root='output_meta')
        output = out.joinpath('tracked_promotions.json')
        print(f'Adding {artifact.name} to tracked list at {output}')
        tracked_promos = json.loads(output.read_text('utf-8')) if output.exists() else {}
        meta = {
            "name": artifact.fullname(),
            "last": {
                "version": artifact.all_versions[-1].version,
                "mc": artifact.all_versions[-1].minecraft_version,
                "timestamp": artifact.all_versions[-1].timestamp.timestamp()
            }
        }
        tracked_promos[artifact.mavenname()] = meta
        writeHashed(out, os.path.basename(output), json.dumps(tracked_promos, indent=2), args.gzip, False)


class PromotionIndexGenerator(Generator):
    def generate(self, md: metadata.Metadata, artifact: metadata.Artifact, tpl: templates.Templates, args: argparse.Namespace):
        out = md.path(root='output_web')
        output = out.joinpath('project_index.html')
        print(f'Generating project index at {output}')
        promos = md.path(root='output_meta').joinpath('tracked_promotions.json')
        tracked_promos = json.loads(promos.read_text('utf-8')) if promos.exists() else {}
        template = tpl.env.get_template('project_index.html')
        writeHashed(out, os.path.basename(output), template.render(md=md, promos=tracked_promos), args.gzip, True)


class RegenGenerator(Generator):
    def generate(self, md: metadata.Metadata, artifact: metadata.Artifact, tpl: templates.Templates, args: argparse.Namespace):
        tracked = md.path(root='output_meta').joinpath('tracked_promotions.json')
        print(f'Re-Generating all projects')
        if (not tracked.exists()):
            print(f'No tracked projects at {tracked}')
            return
        for key in json.loads(tracked.read_text('utf-8')):
            art = metadata.Artifact.load_maven_xml(md, key)
            for gen in Generators['gen']:
                gen.generate(md, art, tpl, args)
        for gen in Generators['index']:
            gen.generate(md, None, tpl, args)

basegens = [MetaJsonGenerator(), MavenJsonGenerator(), IndexGenerator()]
Generators: dict[str, list[Generator]] = {
    'gen': basegens,
    'promote': [PromoteGenerator(), TrackingGenerator(), PromotionIndexGenerator(), *basegens],
    'index': [PromotionIndexGenerator()],
    'regen': [RegenGenerator()]
}
