import os
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.engine.url import URL
from . import base
from .. import utils


REDCAP_DATABASE_NAME = 'redcap'
DEFAULT_SECTION = 'General'


class Client(base.Client):
    name = 'REDCap MySQL'

    description = '''
        Generator for a REDCap project extracted directly from the MySQL
        database.
    '''

    options = {
        'required': ['project'],

        'properties': {
            'project': {
                'description': 'Name of the project.',
                'type': 'string',
            },
            'host': {
                'description': 'Host of the server.',
                'type': 'string',
                'default': 'localhost',
            },
            'port': {
                'description': 'Port of the server.',
                'type': 'number',
                'default': 3306,
            },
            'user': {
                'description': 'Username for authentication.',
                'type': 'string',
            },
            'password': {
                'description': 'Password for authentication',
                'type': 'string',
            }
        }
    }

    def setup(self):
        # Construct engine URL
        url = URL('mysql+pymysql',
                  username=self.options.user,
                  password=self.options.password,
                  host=self.options.host,
                  port=self.options.port,
                  database=REDCAP_DATABASE_NAME)

        self.engine = create_engine(url)

    def parse_user(self, attrs):
        attrs['origins:id'] = attrs['username']
        attrs['prov:label'] = '{} {}'.format(attrs['first_name'],
                                             attrs['last_name'])

        return attrs

    def parse_project_roles(self, project):
        """Fetches, parses, and adds the users attributed to this project
        for their role in the project. This is not an association since no
        explicit activity is involved, but simply attribution to the user
        for the role they serve.
        """

        sql = text('''
            SELECT users.user_firstname as first_name,
                users.user_lastname as last_name,
                users.username as username,
                users.user_email as email,
                group_concat(distinct roles.role_name) as role
            FROM redcap_user_roles roles
                INNER JOIN redcap_user_rights rights
                    ON (roles.role_id = rights.role_id)
                INNER JOIN redcap_user_information users
                    ON (lower(rights.username) = lower(users.username))
            WHERE roles.project_id = :project_id
            GROUP BY first_name, last_name, username, email
        ''')

        query = self.engine.execute(sql, project_id=project['id'])
        keys = query.keys()

        for row in query:
            user = dict(zip(keys[:-1], row[:-1]))

            # Everything but the last item (the role)
            user = self.parse_user(user)

            self.document.add('agent', user)

            # Attribute to the user for the various roles they serve.
            self.document.add('wasAttributedTo', {
                'prov:entity': project,
                'prov:agent': user,
                'prov:type': row[-1].split(','),
            })

    def parse_project(self):
        sql = text('''
            SELECT project_id as id,
                project_name as name,
                app_title as label,
                institution,
                site_org_type as organization,
                project_irb_number as irb_number,
                project_grant_number as grant_number,
                creation_time,
                production_time,
                date_deleted,
                u.user_firstname as creator_firstname,
                u.user_lastname as creator_lastname,
                u.username as creator_username,
                u.user_email as creator_email,
                project_contact_name,
                project_contact_email,
                project_contact_prod_changes_name,
                project_contact_prod_changes_email,
                project_pi_firstname,
                project_pi_mi,
                project_pi_lastname,
                project_pi_email,
                project_pi_username
            FROM redcap_projects p
                LEFT OUTER JOIN redcap_user_information u
                    ON (p.created_by = u.ui_id)
            WHERE project_name = :project
        ''')

        # ResultProxy; supports iteration
        query = self.engine.execute(sql, project=self.options.project)
        keys = query.keys()

        row = list(query)[0]

        # Project entity, first ten columns
        project = dict(zip(keys[:7], row[:7]))
        project['origins:id'] = project['name']
        project['prov:label'] = project['label']
        project['prov:type'] = 'Project'

        # Convert times to timestamps
        created_time = utils.dt_to_timestamp(row[7])
        production_time = utils.dt_to_timestamp(row[8])
        deleted_time = utils.dt_to_timestamp(row[9])

        self.document.add('entity', project)

        # Activity for creating the project
        activity = {
            'origins:id': 'creation:{}'.format(project['origins:id']),
            'prov:label': 'Create project',
            'prov:startTime': created_time,
            'prov:endTime': created_time,
        }

        self.document.add('activity', activity)

        # Project creator
        if row[12]:
            creator = {
                'first_name': row[10],
                'last_name': row[11],
                'username': row[12],
                'email': row[13],
            }

            creator['origins:id'] = creator['username'].lower()  # username
            creator['prov:label'] = '{} {}'.format(creator['first_name'],
                                                   creator['last_name'])

            self.document.add('agent', creator)

            # Attribute
            self.document.add('wasAttributedTo', {
                'prov:agent': creator,
                'prov:entity': project,
                'prov:type': 'Creation',
            })

            # Creator associated with the generation
            self.document.add('wasAssociatedWith', {
                'prov:agent': creator,
                'prov:activity': activity,
                'prov:role': ['Creator'],
            })

        # Generation event of this project
        self.document.add('wasGeneratedBy', {
            'origins:id': project['origins:id'],
            'prov:entity': project,
            'prov:activity': activity,
            'prov:time': created_time,
        })

        # Add the activity for moving the project to production
        if production_time:
            self.document.add('activity', {
                'origins:id': 'production:{}'.format(project['origins:id']),
                'prov:label': 'Move to production',
                'prov:startTime': production_time,
                'prov:endTime': production_time,
            })

        # Project is deleted
        if deleted_time:
            activity = {
                'origins:id': 'deletion:{}'.format(project['origins:id']),
                'prov:label': 'Delete project',
                'prov:startTime': deleted_time,
                'prov:endTime': deleted_time,
            }

            self.document.add('activity', activity)

            self.document.add('wasInvalidatedBy', {
                'prov:activity': activity,
                'prov:entity': project,
            })

        return project

    def get_metadata(self, project):
        sql = text('''
            SELECT
                field_name,
                form_menu_description as form_name,
                element_preceding_header as section_header,
                element_type as field_type,
                element_label as field_label,
                element_note as field_note,
                element_enum as choices_calc_slider,
                branching_logic,
                element_validation_type as validation_type,
                element_validation_min as validation_min,
                element_validation_max as validation_max,
                field_phi as identifier,
                field_req as required,
                custom_alignment,
                question_num as question_number,
                grid_name as matrix_group_name,
                field_order
            FROM redcap_metadata JOIN redcap_projects
                ON (redcap_metadata.project_id = redcap_projects.project_id)
            WHERE redcap_projects.project_id = :project_id
            ORDER BY field_order
        ''')

        query = self.engine.execute(sql, project_id=project['id'])
        keys = query.keys()

        return [dict(zip(keys, row)) for row in query]

    def parse_form(self, project, attrs):
        name = attrs['form_name']

        return {
            'origins:id': os.path.join(project['origins:id'], name),
            'prov:label': utils.prettify_name(name),
            'prov:type': 'Form',
            'name': name,
        }

    def parse_section(self, form, attrs):
        name = attrs['section_header'] or DEFAULT_SECTION

        stripped_name = utils.strip_html(name)

        return {
            'origins:id': os.path.join(form['origins:id'], stripped_name),
            'prov:label': stripped_name,
            'prov:type': 'Section',
            'name': attrs['section_header'],
        }

    def parse_field(self, section, attrs):
        attrs['origins:id'] = os.path.join(section['origins:id'],
                                           attrs['field_name'])
        attrs['prov:label'] = utils.strip_html(attrs['field_label'])
        attrs['prov:type'] = 'Field'

        return attrs

    def parse(self):
        project = self.parse_project()

        self.parse_project_roles(project)

        form = None
        section = None

        for attrs in self.get_metadata(project):
            # No form being handled or a new form is being entered. The form
            # name is only present on the first field in the form.
            if not form or (attrs['form_name'] and
                            attrs['form_name'] != form['name']):
                form = self.parse_form(project, attrs)
                self.document.add('entity', form)

                # Reset section
                section = None

                self.document.add('wasInfluencedBy', {
                    'prov:influencer': project,
                    'prov:influencee': form,
                    'prov:type': 'origins:Edge',
                })

            # An explicit section is present, switch to section. Otherwise
            # if this is the first section for the form, used the default
            # section name.
            name = attrs['section_header']

            if not section or (name and name != section['name']):
                section = self.parse_section(form, attrs)
                self.document.add('entity', section)

                self.document.add('wasInfluencedBy', {
                    'prov:influencer': form,
                    'prov:influencee': section,
                    'prov:type': 'origins:Edge',
                })

            field = self.parse_field(section, attrs)
            self.document.add('entity', field)

            self.document.add('wasInfluencedBy', {
                'prov:influencer': section,
                'prov:influencee': field,
                'prov:type': 'origins:Edge',
            })
