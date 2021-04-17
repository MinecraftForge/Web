from __future__ import annotations

import datetime
import json
import pathlib
import pprint
import re
from collections import defaultdict
from dataclasses import dataclass, field, InitVar
from mc_version import MCVer
import xml.etree.ElementTree as elementtree

MINECRAFT_REG = re.compile(r'^(?P<mcversion>1(?:\.\d+){1,2}?(?:_pre\d+)?)-(?P<rest>[\w]+)$')
VERSION_REG = re.compile(r'^(?P<mcversion>1(?:\.\d+){1,2}?(?:_pre\d+)?)-?(?P<version>(?:\d+(?:\.|\+))*[\d]+)-?(?P<branch>[\w\.\-]+)?$')


def parse_version(version):
    return (versmatch.groupdict().get('mcversion', 'default'), versmatch.group('version'), versmatch.group('branch')) if (versmatch := VERSION_REG.match(version)) else ('default', version, None)


def parse_artifact(artifact: str):
    return artifact.rsplit(":")


SKIP_SUFFIXES = {'.pom', '.sha1', '.md5', '.url', '.asc', '.sha256', '.sha512', '.module'}


@dataclass
class Metadata:
    path_root: pathlib.Path
    output_meta: pathlib.Path
    output_web: pathlib.Path
    web_root: str
    dl_root: str
    static_root: str
    config_path: InitVar[pathlib.Path] = None
    global_config: dict = field(default_factory=dict)
    empty_root: pathlib.Path = pathlib.Path('/')

    def __post_init__(self, config_path):
        self.global_config = json.loads(config_path.read_bytes())

    def path(self, root='path_root', *path):
        return getattr(self, root).joinpath(*path)


@dataclass
class ArtifactItem:
    """Artifact item"""
    version: ArtifactVersion
    filepath: pathlib.Path
    name: str
    classifier: str
    ext: str
    relative_path: str
    timestamp: datetime.datetime = field(init=False)
    sha1: str = ''
    md5: str = ''

    def __post_init__(self):
        self.timestamp = datetime.datetime.fromtimestamp(self.filepath.stat().st_mtime)
        self.sha1 = f.read_text('utf-8') if (f := self.filepath.parent.joinpath(self.name+'.sha1')).exists() else None
        self.md5 = f.read_text('utf-8') if (f := self.filepath.parent.joinpath(self.name+'.md5')).exists() else None

    @classmethod
    def load(cls, artifact_version, file):
        if file.suffix in SKIP_SUFFIXES:
            return None
        if not file.stem.startswith(artifact_version.full_name()):
            return None
        return ArtifactItem(artifact_version, file, file.name, pfx[1:] if len(pfx := file.stem.removeprefix(artifact_version.full_name())) > 0 else '', file.suffix[1:], str(file.relative_to(artifact_version.artifact.metadata.path_root)))


@dataclass
class ArtifactVersion:
    """Artifact Version"""
    artifact: Artifact
    raw_version: str
    version: str
    minecraft_version: str or None
    branch: str or None
    promotion_tags: list[str] = field(init=False, default_factory=list)
    items: list[ArtifactItem] = field(init=False)
    item_by_cls: dict[str, ArtifactItem] = field(init=False)
    timestamp: datetime.datetime = None

    @classmethod
    def load(cls, artifact, version):
        (mcvers, vers, branch) = parse_version(version)
        if vers.endswith('-SNAPSHOT'):
            return
        if not (d := artifact.path().joinpath(version)).exists():
            return
        av = ArtifactVersion(artifact, version, vers, mcvers, branch)
        av.items = [ai for file in d.iterdir()  if (ai := ArtifactItem.load(av, file)) is not None]
        av.item_by_cls = {ai.classifier: ai for ai in av.items}
        av.timestamp = min(ai.timestamp for ai in av.items)
        return av

    def path(self, root='path_root') -> pathlib.Path:
        return self.artifact.path(root).joinpath(self.raw_version)

    def full_name(self):
        return f'{self.artifact.name}-{self.raw_version}'

    def has_promotions(self):
        return len(self.promotion_tags) > 0


@dataclass
class Artifact:
    """Artifact"""
    metadata: Metadata
    group: str
    name: str
    versions: dict[str, dict[str, ArtifactVersion]] = field(init=False)
    all_versions: list[ArtifactVersion] = field(init=False)
    promotions: dict = field(init=False, default_factory=lambda: defaultdict(lambda: defaultdict(str)))
    config: dict = field(init=False, default_factory=dict)

    def fullname(self):
        return self.config.get('name', self.name)

    def path(self, root='path_root') -> pathlib.Path:
        return self.metadata.path(root, self.group.replace('.', '/'), self.name)

    def attach_promotions(self, promotions):
        for key, value in promotions.get('promos', {}).items():
            if mc_match := MINECRAFT_REG.match(key):
                mc_vers = mc_match.group('mcversion')
                tag = mc_match.group('rest').upper()
                if v := self.versions[mc_vers].get(value):
                    self.promotions[mc_vers][tag] = value
                    v.promotion_tags.append(tag)

    def find_version(self, version: str) -> ArtifactVersion:
        v = next((v for v in self.all_versions if v.version == version), None)
        if not v:
            raise ValueError(f'Failed to find {version} in {self.name}')
        return v

    def promote(self, version, tag):
        tag = tag.upper()
        v = self.find_version(version)

        if existing := self.promotions[v.minecraft_version][tag]:
            self.find_version(existing).promotion_tags.remove(tag)

        self.promotions[v.minecraft_version][tag] = version
        v.promotion_tags.append(tag)

    def attach_config(self, config):
        self.config.update(config)

    def parts(self, global_context: dict):
        if len(self.versions) > 1:
            sorted_mc_versions = sorted(self.versions.keys(), reverse=True, key=lambda a: MCVer(a))
            first_idx = next((mc for mc in sorted_mc_versions if 'RECOMMENDED' in self.promotions.get(mc, [])), sorted_mc_versions[0])
            yield 'index.html', global_context | {'mc_version': first_idx, 'mcversions': sorted_mc_versions}
            for mc_version in sorted_mc_versions:
                yield f'index_{mc_version}.html', global_context | {'mc_version': mc_version, 'mcversions': sorted_mc_versions}
        else:
            yield 'index.html', global_context


    @classmethod
    def load_maven_xml(cls, metadata: Metadata, artifact):
        (group, name) = parse_artifact(artifact)
        artifact = Artifact(metadata, group, name)
        try:
            with artifact.path().joinpath('maven-metadata.xml').open('rb') as f:
                artifact.all_versions = sorted(
                    (av for v in elementtree.parse(f).getroot().findall("./versioning/versions/version")
                    if (av := ArtifactVersion.load(artifact, v.text)) is not None), key=lambda v: v.timestamp)
                mc_versions = (av.minecraft_version for av in artifact.all_versions)
                artifact.versions = {mc_version: {av.version: av for av in artifact.all_versions if av.minecraft_version == mc_version} for mc_version in mc_versions}
            promotions = {}
            if (promotions_file := artifact.path().joinpath('promotions_slim.json')).exists():
                promotions |= json.loads(promotions_file.read_bytes())
            if (promotions_file := artifact.path(root='output_meta').joinpath('promotions_slim.json')).exists():
                promotions |= json.loads(promotions_file.read_bytes())
            artifact.attach_promotions(promotions)
            # load local config
            if (config_file := artifact.path().joinpath('page_config.json')).exists():
                artifact.attach_config(json.loads(config_file.read_bytes()))
            # overwrite global config values
            artifact.attach_config(metadata.global_config)
        except Exception as e:
            raise RuntimeError('Failed to load and parse maven-metadata.xml', e)
        return artifact
