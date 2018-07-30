from flask import abort, jsonify, make_response, request

from ota_api.ota_user import OTAUserBase


class FauxUser(OTAUserBase):
    def __init__(self):
        # this is a dumb example and there's a circular dependency between
        # app.py and this file:
        from oauthful.app import USER_TOKENS
        key = request.headers.get('OTA-TOKEN', None)
        if not key or key not in USER_TOKENS.values():
            abort(make_response(
                jsonify(message='Authorization required'), 401))

    @property
    def max_devices(self):
        return 10
