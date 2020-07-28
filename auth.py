import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'loginpath.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'cast'

'''
Exception for Auth errors
'''

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code 

def get_token_auth_header():
    '''This function obtains the access token from the Authorization Header
    '''
    auth = request.headers.get('Authorization', None)

    if not auth:
        print('not auth')
        raise AuthError({
            'code': 'authorization header_missing',
            'description': 'Authorization header is expected'}, 401)
    
    parts = auth.split()

    if parts[0].lower() != 'bearer':
        print('no bearer')
        raise AuthError({
        'code': 'invalid_header',
        'description': 'Authorization header must start with Bearer.'}, 
        401)

    elif len(parts) == 1:
        print('no token')
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found'}, 401)
    
    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token'},
            401)
    
    token = parts[1]
    return token

def check_permissions(permission, payload):
    '''This function checks the permissions that are in the 
    JWT to see if the request permission is in the request'''

    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'},
            400)
    
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'}, 403)
    
    return True 

def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        print('invalid header')
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed'}, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    
    if rsa_key:
        try: 
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms = ALGORITHMS,
                audience = API_AUDIENCE,
                issuer = 'https://' + AUTH0_DOMAIN + '/'
            )
            return payload

        except jwt.ExpiredSignatureError:
            print('expired token')
            raise AuthError({
                'code': 'token_expired',
                'description': 'token expired'})
        
        except jwt.JWTClaimsError:
            print('incorrect claims')
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please check the audience and the issuer'
        }, 401)

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropiate key'},
                400)
    raise AuthError({
                    'code': 'invalid_header',
                    'description': 'Unable to find the appropiate key'}, 400)

def requires_auth(permissions=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                print('could not verify_decode_jwt')
                abort(401)
            check_permissions(permissions, payload)
            return f(payload, *args, **kwargs)
        return wrapper 
    return requires_auth_decorator