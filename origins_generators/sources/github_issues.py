import requests
from ..utils import timestr_to_timestamp
from . import base


GITHUB_V3_ACCEPT_MIMETYPE = 'application/vnd.github.v3+json'
GITHUB_V3_ISSUES_URL = 'https://api.github.com/repos/{owner}/{repo}/issues'


class Client(base.Client):
    name = 'GitHub Issues'

    description = 'Client for extracting GitHub issues.'

    options = {
        'required': ['owner', 'repo'],

        'properties': {
            'owner': {
                'description': 'The owner of the repository.',
                'type': 'string',
            },
            'repo': {
                'description': 'The name of the repository.',
                'type': 'string',
            },
            'params': {
                'description': 'Set of key/value GET parameters amended to '
                               'the URL. For a list of available parameters, '
                               'see: https://developer.github.com/v3/issues/#parameters-1',  # noqa
                'type': 'object',
            },
            'token': {
                'description': 'API token for private repositories',
                'type': 'string',
            },
        }
    }

    def _send_request(self, url):
        headers = {
            'Accept': GITHUB_V3_ACCEPT_MIMETYPE,
        }

        if self.options.token:
            headers['Authorization'] = 'token ' + self.options.token

        # Initial request
        resp = requests.get(url, params=self.options.params, headers=headers)
        resp.raise_for_status()

        return resp

    def _get_issues(self):
        url = GITHUB_V3_ISSUES_URL.format(owner=self.options.owner,
                                          repo=self.options.repo)

        resp = self._send_request(url)

        links = resp.links

        for attrs in resp.json():
            yield attrs

        while links and 'next' in links:
            resp = self._send_request(links['next']['url'])
            resp.raise_for_status()

            links = resp.links

            for attrs in resp.json():
                yield attrs

    def parse_user(self, user):
        return {
            'origins:id': user['url'],
            'prov:type': 'User',
            'prov:label': user['login'],
            'id': user['id'],
            'login': user['login'],
            'url': user['url'],
        }

    def parse_issue_entity(self, issue):
        if issue.get('pull_request'):
            issue_type = 'Pull Request'
        else:
            issue_type = 'Issue'

        return {
            'origins:id': issue['url'],
            'prov:type': issue_type,
            'prov:label': issue['title'],
            'body': issue['body'],
            'title': issue['title'],
            'state': issue['state'],
            'number': issue['number'],
            'url': issue['url'],
            'html_url': issue['html_url'],
            'comments': issue['comments'],
            'created_at': issue['created_at'],
            'updated_at': issue['updated_at'],
            'closed_at': issue['closed_at'],
        }

    def parse_issue(self, attrs):
        issue = self.parse_issue_entity(attrs)
        self.document.add('entity', issue)

        # User who opened the issue
        user = self.parse_user(attrs['user'])
        self.document.add('agent', user)

        # Attribution to the user for creating the issue. Id is fixed
        # so redundant attribution is not provided.
        self.document.add('wasAttributedTo', {
            'origins:id': issue['origins:id'],
            'prov:label': '{} Creator'.format(issue['prov:type']),
            'prov:entity': issue,
            'prov:agent': user,
        })

        # Activity of creating the issue.
        activity = {
            'origins:id': issue['origins:id'],
            'prov:type': 'Create {}'.format(issue['prov:type']),
        }

        self.document.add('activity', activity)

        # Association of the user to the creator role
        self.document.add('wasAssociatedWith', {
            'origins:id': issue['origins:id'],
            'prov:role': '{} Creator'.format(issue['prov:type']),
            'prov:agent': user,
            'prov:activity': activity,
        })

        # If this *is* a new issue, we can include the activity
        if issue['updated_at'] and issue['updated_at'] != issue['created_at']:
            time = timestr_to_timestamp(issue['updated_at'])

            gen = {
                'prov:time': time,
                'prov:entity': issue,
            }
        else:
            time = timestr_to_timestamp(issue['created_at'])

            gen = {
                'prov:time': time,
                'prov:entity': issue,
                'prov:activity': activity,
            }

        # Generation for the updated issue. We don't know the activity
        # that caused the change so an activity is not linked to the
        # event.
        self.document.add('wasGeneratedBy', gen)

        # The user assigned to the issue. Since the issue can change
        # independent of the assignee, the id is bound to the user.
        if attrs.get('assignee'):
            user = self.parse_user(attrs['assignee'])
            self.document.add('agent', user)

            attr_id = '{}/{}'.format(issue['origins:id'], user['login'])

            self.document.add('wasAttributedTo', {
                'origins:id': attr_id,
                'prov:label': '{} Assignee'.format(issue['prov:type']),
                'prov:entity': issue,
                'prov:agent': user,
            })

        # The issue is closed. Note this does not invalidate the issue since
        # it can still be modified on the source system (i.e. GitHub)
        if attrs['closed_at']:
            close_id = '{}/close'.format(issue['origins:id'])

            activity = {
                'origins:id': close_id,
                'prov:type': 'Close {}'.format(issue['prov:type']),
                'prov:startTime': timestr_to_timestamp(attrs['closed_at']),
            }

            self.document.add('activity', activity)

            if attrs.get('closed_by'):
                user = self.parse_user(attrs['closed_by'])
                self.document.add('agent', user)

                self.document.add('wasAttributedTo', {
                    'origins:id': close_id,
                    'prov:label': '{} Closer'.format(issue['prov:type']),
                    'prov:entity': issue,
                    'prov:agent': user,
                })

                self.document.add('wasAssociatedWith', {
                    'origins:id': close_id,
                    'prov:agent': user,
                    'prov:activity': activity,
                    'prov:role': 'Closer'
                })

    def parse(self):
        for attrs in self._get_issues():
            self.parse_issue(attrs)
