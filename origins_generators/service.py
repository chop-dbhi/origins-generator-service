import json
from flask import Flask, request, url_for
from .exceptions import UnknownSource, SourceNotSupported
from . import sources, utils


app = Flask(__name__)

DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
}


def jsonify(data):
    if app.debug:
        return json.dumps(data, indent=4, sort_keys=True)

    return json.dumps(data)


@app.route('/', methods=['GET'])
def list_sources():
    items = []

    for name in sources.SOURCES:
        try:
            Client = sources.get(name)
        except Exception:
            continue

        description = utils.remove_newlines(Client.description)

        items.append({
            'name': Client.name,
            'description': description,
            'url': url_for('source', name=name, _external=True),
            'version': Client.version,
        })

    return jsonify(items), 200, DEFAULT_HEADERS


@app.route('/<name>/', methods=['GET', 'POST'])
def source(name):
    try:
        Client = sources.get(name)
    except UnknownSource:
        return '', 404
    except SourceNotSupported:
        return jsonify({
            'message': 'Source not supported',
        }), 422

    if request.method == 'GET':
        description = utils.remove_newlines(Client.description)

        attrs = {
            'name': Client.name,
            'description': description,
            'url': url_for('source', name=name, _external=True),
            'version': Client.version,
            'schema': Client.schema,
        }

        return jsonify(attrs), 200, DEFAULT_HEADERS

    options = request.json

    # Client supports the path option. Check if files have been
    # uploaded and set the path to the file object.
    if 'uri' in Client.options and request.files:
        options['uri'] = request.files['file'].filename

    try:
        client = Client(**options)
    except Exception as e:
        return jsonify({'message': str(e)}), 422

    data = client.generate()

    # Add timestamp and client metadata
    data['_meta'] = {
        'time': utils.timestamp(),
        'client': {
            'name': Client.name,
            'description': Client.description,
            'version': Client.version,
        }
    }

    return jsonify(data), 200, DEFAULT_HEADERS
