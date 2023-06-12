from flask import request, g
from common.utils.mayjwt import verify_token


def jwt_authorization():
    """
    jwt的验证
    :return:
    """
    token = request.headers.get('Authorization')
    print(token)
    if token and token.startswith('JWT '):
        token_ = token[4:]
        print("token_ ---->", token_)
        payload = verify_token(token_)
        print('payload--->', payload)
        if payload:
            g.user_id = payload.get('user_id')