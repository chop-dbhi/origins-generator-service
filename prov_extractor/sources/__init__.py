from importlib import import_module
from ..exceptions import UnknownSource, SourceNotSupported


JSON_SCHEMA_NS = 'http://json-schema.org/draft-04/schema#'


SOURCES = {
    'sqlite': 'prov_extractor.sources.sqlite',
    'postgresql': 'prov_extractor.sources.postgresql',
    'delimited': 'prov_extractor.sources.delimited',
    'filesystem': 'prov_extractor.sources.filesystem',
    'excel': 'prov_extractor.sources.excel',
    'mongodb': 'prov_extractor.sources.mongodb',
    'mysql': 'prov_extractor.sources.mysql',
    'oracle': 'prov_extractor.sources.oracle',
    'vcf': 'prov_extractor.sources.vcf',
    'redcap-mysql': 'prov_extractor.sources.redcap_mysql',
    'redcap-api': 'prov_extractor.sources.redcap_api',
    'redcap-csv': 'prov_extractor.sources.redcap_csv',
    'harvest': 'prov_extractor.sources.harvest',
    'datadict': 'prov_extractor.sources.datadict',
    'github-issues': 'prov_extractor.sources.github_issues',
    'git': 'prov_extractor.sources.git',
}

SOURCE_ALIASES = {
    'redcap': {
        'source': 'redcap-mysql',
    },
    'csv': {
        'source': 'delimited',
        'options': {
            'delimiter': ',',
        }
    },
    'tab': {
        'source': 'delimited',
        'options': {
            'delimiter': '\t',
        }
    }
}


_modules = {}


def get_module(name):
    "Attempts to import a source by name."
    if name in SOURCE_ALIASES:
        name = SOURCE_ALIASES[name]['source']

    if name in _modules:
        return _modules[name]

    module = SOURCES.get(name)

    if not module:
        raise UnknownSource(name)

    try:
        module = import_module(module)
    except ImportError as e:
        raise SourceNotSupported(str(e))

    _modules[name] = module
    return module


def get(name):
    "Returns the client class of a source."
    return get_module(name).Client
