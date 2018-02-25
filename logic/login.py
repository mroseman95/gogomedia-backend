from functools import wraps
from flask import request, jsonify, session, current_app

from models.user import User
from logic.user import get_user_by_id


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = None

        if current_app.config['LOGIN_DISABLED']:
            return f(user, *args, **kwargs)

        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(' ')[1]
            user_id = User.decode_auth_token(auth_token)

            # decode_auth_token returns a string if there was an exception decoding the auth_token
            if isinstance(user_id, str):
                return jsonify({
                    'success': False,
                    'message': user_id
                }), 401

            user = get_user_by_id(user_id)

            return f(user, *args, **kwargs)
        else:
            return jsonify({
                'success': False,
                'message': 'No Authorization header found. Please add auth_token in Authorization header.'
            }), 401

    return decorated_function