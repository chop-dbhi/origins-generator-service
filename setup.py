import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 3, 0):
    raise EnvironmentError('Python version not supported')


kwargs = {
    'name': 'origins-generators',
    'version': __import__('origins_generators').get_version(),
    'description': 'Provenance generator service for Origins.',
    'url': 'https://github.com/chop-dbhi/origins-generators/',
    'author': 'Byron Ruth',
    'author_email': 'b@devel.io',
    'license': 'BSD',
    'keywords': 'provenance generator origins service REST',
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    'packages': find_packages(exclude=['tests']),

    'install_requires': [
        'docopt>=0.6',
        'flask>=0.10,<0.11',
        'requests>=2.4,<2.5',
        'python-dateutil>=2.2,<2.3',
        'jsonschema>=2.4,<2.5'
    ],

    'scripts': ['bin/origins-generators'],
}

setup(**kwargs)
