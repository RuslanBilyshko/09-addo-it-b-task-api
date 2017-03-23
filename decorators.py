from functools import wraps
from flask_login import current_user
from flask import jsonify


# Декоратор для проверки на авторизацию пользователя
def is_auth(function):
    @wraps(function)
    def _wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"auth": False}), 401
        else:
            return function(*args, **kwargs)

    return _wrapper
