__author__ = 'gmena'

import datetime

JWT_EXPIRE = datetime.timedelta(days=1)  # Expire token
JWT_ALG = 'HS256'  # Crypt algorithm
JWT_KID = 'HS_123'  # Key id
JWT_KEY = 'HS_123456'  # Private Secret Key
JWT_HEADER_PREFIX = 'Bearer'  # Http Authorization: Bearer
JWT_RENEW = True
JWS_LEEWAY = 0
