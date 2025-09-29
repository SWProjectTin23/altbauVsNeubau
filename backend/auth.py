import os
import requests
import jwt
from flask import request, jsonify
from functools import wraps

JWKS_URL = os.getenv('JWKS_URL')
CLIENT_ID = os.getenv('CLIENT_ID')

print(CLIENT_ID, JWKS_URL)

def get_public_key(token):
    header = jwt.get_unverified_header(token)
    kid = header['kid']
    jwks = requests.get(JWKS_URL).json()
    for key in jwks['keys']:
        if key['kid'] == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key)
    raise Exception("Public key not found")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        if not token:
            return {"message": "Token is missing"}, 401
        
        try:
            public_key = get_public_key(token)
            decoded = jwt.decode(token, public_key, algorithms=['RS256'], options={"verify_aud": False})
            
            if decoded.get('azp') != CLIENT_ID:
                raise Exception(f"Authorized party mismatch: expected {CLIENT_ID}, got {decoded.get('azp')}")
            
            request.user = decoded
            
        except Exception as e:
            return {"message": "Token is invalid", "error": str(e)}, 401
        
        return f(*args, **kwargs)
    return decorated
