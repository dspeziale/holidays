from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*roles):
    """Decorator RBAC: limita accesso ai ruoli specificati."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator


def admin_required(f):
    return role_required('admin')(f)


def manager_required(f):
    return role_required('admin', 'manager')(f)
