from flask import abort
from functools import wraps
from flask.ext.login import current_user


def admin_required(f):
    """

    :param f: function, which we want to decorate
    :return: decorated function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function