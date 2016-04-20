__author__ = 'gmena'
from jwt.jwt import JWT
from jwt.jwk import JWKSet
from mixin.jwt import JWTSetting
from datetime import datetime

import json
import time


class JWTHandler(object):
    @staticmethod
    def jwt_target(keys):
        return JWT(keys)

    @staticmethod
    def jwt_verify(keys, jwt):
        _jwt = JWT(keys)
        return _jwt.verify(jwt)

    @staticmethod
    def jwt_get_payload(user):
        return json.dumps({
            'user': user.pk,
            'email': user.email,
            'exp': time.mktime((datetime.utcnow() + JWTSetting.JWT_EXPIRE).timetuple())
        })

    @staticmethod
    def jwt_prepare_keys(key=JWTSetting.JWT_KEY):
        keys = JWKSet()
        keys = keys.from_dict({
            'keys': [
                {
                    'kid': JWTSetting.JWT_KID,
                    'kty': JWTSetting.JWT_ALG.startswith('HS') and 'oct' or 'RSA',
                    'k': key
                }
            ]
        })

        return keys

    @staticmethod
    def jwt_encode_handler(keys, payload):
        _jwt = JWT(keys)
        return _jwt.encode({
            "typ": "JWT",
            "alg": JWTSetting.JWT_ALG,
            'kid': JWTSetting.JWT_KID
        }, payload)

    @staticmethod
    def jwt_decode_handler(keys, jwt):
        _jwt = JWT(keys)
        return _jwt.decode(jwt)

    @staticmethod
    def get_authorization_header(request):
        """
        Return request's 'Authorization:' header, as a bytestring.
        From: https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/authentication.py
        """
        auth = request.META.get('HTTP_AUTHORIZATION', b'')

        if isinstance(auth, str):
            # Work around django test client oddness
            auth = auth.encode('iso-8859-1')

        return auth
