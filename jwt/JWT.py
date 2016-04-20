###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Geolffrey Mena
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################
from datetime import datetime
import json
import time

from jwt.jwt import JWT
from jwt.jwk import JWKSet

from jwt import JWTSetting


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
