import os
import fnmatch
from datetime import datetime
from . import base


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


class Client(base.Client):
    name = 'Directory'

    description = '''
        Generator for a filesystem.
    '''

    options = {
        'required': ['path'],

        'properties': {
            'path': {
                'description': 'A local filesystem directory.',
                'type': 'string',
            },
            'recurse': {
                'description': 'If true, directories will be recursed into.',
                'type': 'boolean',
                'default': True,
            },
            'domain': {
                'description': 'The domain for new facts',
                'type': 'string',
                'default': None,
            },
            'valid_time': {
                'description': 'Valid_time for new facts',
                'type': 'string',
                'default': None,
            },
            'pattern': {
                'description': 'Glob pattern for directories and files.',
                'type': 'string',
                'default': '*',
            },
            'hidden': {
                'description': 'If true, hidden files and directories will be included.',  # noqa
                'type': 'boolean',
                'default': False,
            },
            'depth': {
                'description': 'The maximum depth to recurse into.',
                'type': 'integer',
            }
        }
    }

    def parse_directory(self, path):
        path_id = os.path.relpath(path, self.options.path)

        return {
            'id': path_id,
        }

    def parse_file(self, path):
        path_id = os.path.relpath(path, self.options.path)

        stats = os.stat(path)

        # Convert into datetime from timestamp floats
        atime = datetime.fromtimestamp(stats.st_atime)
        mtime = datetime.fromtimestamp(stats.st_mtime)

        if hasattr(stats, 'st_birthtime'):
            create_time = stats.st_birthtime
        else:
            create_time = stats.st_ctime

        ctime = datetime.fromtimestamp(create_time)

        return {
            'id': path_id,
            'mode': stats.st_mode,
            'uid': stats.st_uid,
            'gid': stats.st_gid,
            'size': stats.st_size,
            'accessed': atime.strftime(DATETIME_FORMAT),
            'modified': mtime.strftime(DATETIME_FORMAT),
            'created': ctime.strftime(DATETIME_FORMAT),
        }

    def parse(self):
        print('-----------')
        print('FILESYSTEM')
        print('-----------')
        base_path = self.options.path
        yield [
            'operation',
            'domain',
            'entity',
            'attribute'
            'value',
            'valid_time'
        ]

        for root, dirs, names in os.walk(base_path):
            if self.options.depth is not None:
                curpath = os.path.relpath(root, base_path)

                if curpath == '.':
                    depth = 0
                else:
                    depth = len(curpath.split(os.path.sep))

                # Remove all subdirectories from traversal once the
                # desired depth has been reached. Note a `break` does
                # not work since this would stop processing sibling
                # directories as well.
                for dirname in dirs[:]:
                    if depth >= self.depth:
                        dirs.pop()
                    elif not self.options.hidden and dirname.startswith('.'):
                        dirs.pop() 

            directory = self.parse_directory(root)

            for i, f in enumerate(fnmatch.filter(names, self.options.pattern)):
                if not self.options.hidden and f.startswith('.'):
                    continue
                file = self.parse_file(os.path.abspath(os.path.join(
                                                                        base_path,
                                                                        directory['id'],
                                                                        f
                                                                    )))
                for key, value in file.items():
                    yield [
                        'assert',
                        self.options.domain,
                        os.path.join(directory['id'], f),
                        key,
                        value,
                        self.options.valid_time
                    ]

                yield [
                    'assert',
                    self.options.domain,
                    directory['id'],
                    'file',
                    f,
                    self.options.valid_time
                ]
