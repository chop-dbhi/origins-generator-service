import shutil
import tempfile
import subprocess
from . import base


def clone_repo(uri, branch):
    tmp = tempfile.mkdtemp()

    subprocess.check_call([
        'git',
        'clone',
        uri,
        '--branch',
        branch,
        '--single-branch',
        tmp,
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return tmp


def get_all_files(repo):
    lines = subprocess.check_output([
        'git',
        '-C',
        repo,
        '--no-pager',
        'log',
        '--pretty=format:',
        '--name-only',
        '--diff-filter=A'
    ]).decode('utf-8')

    return set(l for l in lines.split('\n') if l)


# Git log for each file to find out about all commits, authors, the commit
# parents, and the modification type.
def get_file_commits(repo, fpath):
    lines = subprocess.check_output([
        'git',
        '-C',
        repo,
        '--no-pager',
        'log',
        '--reverse',
        '--date=iso',
        '--name-status',
        '--pretty=format:%H||%P||%an||%ad||%cn||%cd||%s||&',
        '--',
        fpath,
    ]).decode('utf-8')

    commits = []
    lines = lines.replace('||&\n', '||').split('\n')

    for line in lines:
        if not line:
            continue

        toks = line.split('||')

        commit = {
            'sha1': toks[0],
            'entity': fpath,
            'parents': [p for p in toks[1].split(' ') if p],
            'author': toks[2],
            'author_date': toks[3],
            'committer': toks[4],
            'commit_date': toks[5],
            'subject': toks[6],
            'mod_type': toks[7][0],  # first character
        }

        commits.append(commit)

    return commits


class Client(base.Client):
    name = 'Git'

    description = '''
        Generator for Git repositories.
    '''

    options = {
        'required': ['uri'],

        'properties': {
            'uri': {
                'description': 'URI to a Web accessible Git repository or local path.',  # noqa
                'type': 'string',
            },
            'branch': {
                'description': 'The branch that will be cloned and converted',
                'type': 'string',
                'default': 'master',
            }
        }
    }

    def setup(self):
        self.repo_dir = clone_repo(self.options.uri, self.options.branch)

    def parse_file(self, fname):
        commits = get_file_commits(self.repo_dir, fname)

        previous = None
        previous_id = None

        for commit in commits:
            sha1 = commit['sha1']

            # The commit itself
            activity_id = sha1

            activity = {
                'origins:id': activity_id,
                'prov:label': commit['subject'],
                'prov:startTime': commit['author_date'],
                'prov:endTime': commit['commit_date'],
            }

            # The author of the commit
            author_id = commit['author']

            author = {
                'origins:id': author_id,
                'prov:label': commit['author'],
            }

            # The file affected by the commit
            entity_id = '{}:{}'.format(sha1, fname)

            entity = {
                'origins:id': entity_id,
                'prov:label': fname,
                'prov:type': 'File',
                'sha1': sha1,
                'parents': commit['parents'],
            }

            self.document.add('activity', activity)
            self.document.add('agent', author)
            self.document.add('entity', entity)

            # Authorship of the commit
            self.document.add('wasAttributedTo', {
                'origins:id': '{}:{}'.format(entity_id, author_id),
                'prov:entity': entity,
                'prov:agent': author,
                'prov:type': 'Authorship'
            })

            # Reference so the committer role can be added if applicable
            author_roles = ['Author']

            self.document.add('wasAssociatedWith', {
                'origins:id': '{}:{}'.format(author_id, activity_id),
                'prov:agent': author,
                'prov:activity': activity,
                'prov:role': author_roles,
            })

            if commit['author'] == commit['committer']:
                author_roles.append('Committer')
            else:
                committer_id = commit['committer']

                committer = {
                    'origins:id': committer_id,
                    'prov:label': commit['committer'],
                }

                self.document.add('agent', committer)

                self.document.add('wasAssociatedWith', {
                    'origins:id': '{}:{}'.format(committer_id, activity_id),
                    'prov:activity': activity,
                    'prov:agent': committer,
                    'prov:role': 'Committer',
                })

            # Delete
            if commit['mod_type'] == 'D':
                self.document.add('wasInvalidatedBy', {
                    'origins:id': '{}:{}'.format(sha1, fname),
                    'prov:entity': entity,
                    'prov:activity': activity,
                    'prov:time': commit['author_date'],
                })
            # Add
            else:
                # Generation of the entity, so the entity_id is used
                generation = {
                    'origins:id': entity_id,
                    'prov:entity': entity,
                    'prov:activity': activity,
                    'prov:time': commit['author_date'],
                }

                self.document.add('wasGeneratedBy', generation)

                # If this is a change, add derivation between parent and commit
                if commit['mod_type'] != 'A':
                    # Previous entity was used for a derivation in this
                    # commit
                    usage = {
                        'origins:id': '{}:{}'.format(sha1, previous_id),
                        'prov:activity': activity,
                        'prov:entity': previous,
                        'prov:time': commit['author_date'],
                    }

                    # Derivation of the current entity from the previous state
                    derivation = {
                        'origins:id': '{}:{}'.format(previous_id, entity_id),
                        'prov:activity': activity,
                        'prov:generatedEntity': entity,
                        'prov:usedEntity': previous,
                        'prov:generation': generation,
                        'prov:usage': usage,
                        'prov:type': 'prov:Revision',
                    }

                    self.document.add('used', usage)
                    self.document.add('wasDerivedFrom', derivation)

            previous = entity
            previous_id = entity_id

    def parse(self):
        files = get_all_files(self.repo_dir)

        for fname in files:
            self.parse_file(fname)

        shutil.rmtree(self.repo_dir)
