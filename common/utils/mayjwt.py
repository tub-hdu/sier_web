import jwt
import traceback

from datetime import datetime, timedelta
from flask import app, current_app, g


def generate_jwt(payload, expiry, secret=None):
    """
    生成jwt
    :param payload: dict 荷载信息
    :param expiry: date  有效期
    :param secret: str  盐
    :return:  token
    """
    _payload = {
        'exp': expiry
    }
    token = None
    try:
        _payload.update(payload)
        if not secret:
            secret = current_app.config['JWT_SECRET']
        # 生成token       _payload 荷载信息：用户账号信息、 有效期   secret 盐
        token = jwt.encode(_payload, secret, algorithm='HS256')
    except Exception as e:
        error = traceback.format_exc()
        print('generate_jwt is error:{}'.format(error))
    return token


# 校验token
def verify_token(token,secret=None,algorithm='HS256'):
    """
        校验token
        :param token: 传递来的token
        :param secret: 每个项目的私钥, 要在配置文件中存放
        :param algorithm: 加密算法
        :return: payload 用户信息部分
        """
    payload = None
    if not secret:
        # 从配置文件中读取SECRET_KEY
        secret = current_app.congfig.get('SECRET_KEY')
    try:
        payload = jwt.decode(token,secret,algorithms=algorithm)
    except Exception as e:
        payload = None
    return payload


# # 生成Token
def _generate_token(account, user_id, refresh=True):
    """
    生成token
    :param user_id:
    :return:
    """
    # 获取盐
    secret = current_app.config.get('SECRET_KEY')
    # 定义过期时间: 2小时有效期
    expiry = datetime.utcnow() + timedelta(hours=2)
    # 生成Token
    token = 'JWT' + generate_jwt({'username': account, 'user_id': user_id}, expiry, secret).decode()
    print("ADSFAF",token)
    print("adsfasdf", type(account))
    if refresh:
        # 生成新token, 无感知刷新
        expiry = datetime.utcnow() + timedelta(days=15)
        # is_refresh作为更新token的信号
        refresh_token = 'JWT' + generate_jwt({'username': account, 'user_id': user_id,
                                                'is_refresh': True}, expiry,secret).decode()
    else:
        refresh_token = None
    return token, refresh_token


def refresh_token():
    """
    刷新token
    :return:
    """
    if g.account is not None and g.is_refresh is True:
        token, _ = _generate_token(g.account, g.user_id, refresh=False)
        return {'message': 'ok', 'data': {'token': token}, 'code': 200}
    else:
        return {'message': 'Invalid refresh token', 'code': 500}