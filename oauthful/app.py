'''
I call this "oauthful" because its an awful way to do oauth. However, it
does convey the clear path to securing your OTA Community Edition server.
'''

from base64 import b64decode

from flask import Flask, jsonify, make_response, request
from werkzeug.exceptions import BadRequest, Unauthorized

app = Flask(__name__)


USER_TOKENS = {
    # <client_id>:<client_secret>
    '7a455f3b-2234-43b5-9d13-7d8823494f21:OTbGcZx6my': 'BadT0ken5',
}


@app.route('/token', methods=('POST',))
def create_token():
    gt = request.form['grant_type']
    if gt != 'client_credentials':
        raise BadRequest('Invalid grant type: ' + gt)

    auth = request.headers['Authorization']
    try:
        method, value = auth.split(' ', 1)
    except ValueError:
        raise BadRequest('Invalid Authorization header')
    value = b64decode(value.strip().encode()).decode()

    if method == 'Basic':
        token = USER_TOKENS.get(value)
        if token:
            return jsonify({'access_token': token})
        raise Unauthorized('Unknown client-id or client-secret')

    raise BadRequest('Invalid Authorization method: ' + method)


@app.route('/auth-token', methods=('GET',))
def auth_token():
    try:
        auth = request.headers['Authorization']
    except KeyError:
        raise Unauthorized('No auth header provided')
    try:
        method, value = auth.split(' ', 1)
    except ValueError:
        raise BadRequest('Invalid Authorization header')
    if method == 'Bearer':
        if value in USER_TOKENS.values():
            return 'OK'
        raise Unauthorized('Unknown user')

    raise BadRequest('Invalid Authorization method: ' + method)


@app.route('/auth-basic', methods=('GET',))
def auth_basic():
    try:
        auth = request.headers['Authorization']
    except KeyError:
        headers = {'WWW-Authenticate': 'Basic realm"Login Required"'}
        return make_response('Authorization Required', 401, headers)
    try:
        method, value = auth.split(' ', 1)
    except ValueError:
        raise BadRequest('Invalid Authorization header')
    if method == 'Basic':
        value = b64decode(value.strip().encode()).decode()
        _, token = value.split(':', 1)
        if token in USER_TOKENS.values():
            return 'OK'
        raise Unauthorized('Unknown user')

    raise BadRequest('Invalid Authorization method: ' + method)
