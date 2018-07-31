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

    def _get(self, name):
        if name == 'arbitrary':
            # A device named "arbitrary" can be listed, but not
            # viewed (GET /devices/arbitrary/) or updated
            abort(make_response(
                jsonify(message='I will not allow this'), 403))


'''
 An alternative way you could display device details. Just as an example:
    def device_list(self):
        api = OTACommunityEditionAPI('default')
        for d in api.device_list():
            yield self._format_device(api, d, False)

    def device_get(self, name):
        api, d = self._get(name)
        return self._format_device(api, d, True)

    def _format_device(self, api, device, detailed):
        d = {
            'id': device['uuid'],
            'name': device['deviceName'].split('/', 1)[1],
            'stream': device['namespace'],
            'created': device['createdAt'],
            'last-seen': device['lastSeen'],
            'status': device['deviceStatus'],
            'image': self._device_image(api, device)
        }
        if detailed:
            d['hardware'] = api.device_hardware(device)
            d['network'] = api.device_network(device)
            if d['image']['ecu'] != '?':
                d['autoUpdates'] = api.device_autoupdates_enabled(
                    device, d['image']['ecu'])
            else:
                # The device has never been seen before
                d['autoupdates'] = False
        return d
'''
