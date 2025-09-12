import os
import requests
import jwt
from flask import request, jsonify
from functools import wraps

JWKS_URL = f"{os.getenv('JWKS_URL')}"
CLIENT_ID = f"{os.getenv('CLIENT_ID')}"

print(JWKS_URL)
jwks = requests.get(JWKS_URL).json()

def get_public_key(token):
    header = jwt.get_unverified_header(token)
    kid = header['kid']
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
            return jsonify({"message": "Token is missing"}), 401
        try:
            public_key = get_public_key(token)
            decoded = jwt.decode(token, public_key, algorithms=['RS256'], audience=CLIENT_ID)
            request.user = decoded
        except Exception as e:
            return jsonify({"message": "Token is invalid", "error": str(e)}), 401
        return f(*args, **kwargs)
    return decorated
