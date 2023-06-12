from flask import g, request
from functools import wraps

from common.models import rds


def login_required(func):
    """
    强制登录的装饰器
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if g.user_id is not None:
            return func(*args, **kwargs)
        return {'code': 401, 'message': 'Invalid token account is none'}
    return wrapper


def superuser(func):
    """ 权限验证装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if list(set(g.role_id) & set(list([1, 2]))):
            print("1121252", g.vid)
            return func(*args, **kwargs)
        return {'code': 401, 'message': '无权限'}
    return wrapper