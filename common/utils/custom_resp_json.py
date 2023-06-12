from flask_restful.representations.json import output_json
from flask import make_response, current_app
from flask_restful.utils import PY3
from json import dumps


def custom_json(data, code, headers=None):
    """自定义返回的json数据"""
    if 'message' not in data:
        data = {
            'message': 'ok', # 这个是写死的,现在没有办法自定义
            'data': data
        }
    if 'code' not in data:
        data.update({'code': code})

    settings = current_app.config.get('RESTFUL_JSON', {})

    if current_app.debug:
        settings.setdefault('indent', 4)
        settings.setdefault('sort_keys', not PY3)

    dumped = dumps(data, **settings) + "\n"

    resp = make_response(dumped, code)
    resp.headers.extend(headers or {})
    return resp