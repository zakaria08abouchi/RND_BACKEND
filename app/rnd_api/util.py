import jwt
import uuid
from flask import jsonify, make_response, request
from functools import wraps
from rnd_api import app
from rnd_api.models import User



# Tokens section------------------------------------------------------------------------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        else:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token.replace('"', ''), app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)

    return decorated


    