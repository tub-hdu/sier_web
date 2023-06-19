import requests
import base64
import hmac
import urllib
from hashlib import sha256
import time, json
from urllib.parse import parse_qs, urlencode
from flask import Blueprint, current_app, jsonify
from flask_restful import Api, Resource, reqparse
from werkzeug.security import check_password_hash

from common.models.user_model import OauthUser, UserModels, db
from common.utils.mayjwt import _generate_token


oauth_user_bp = Blueprint('oauth_bp', __name__,url_prefix='/oauth2')

api = Api(oauth_user_bp)


class OauthUserr(Resource):
    def get(self):
        """
        生成qq扫码登录的url,返回给前端用户
        :params: response_type=code # 扫码登录
        :params: state, redirect_uri
        :return:
        https://graph.qq.com/oauth2.0/show?which=Login&display=pc&response_type=code&state=9B93F12415BCB93941FDA383B66278470B75111C8D2BDC15474EF49E12D42E28F4FBBFC996B3C21250B8B7D1F915AA0A&client_id=100273020&redirect_uri=https%3A%2F%2Fqq.jd.com%2Fnew%2Fqq%2Fcallback.action%3Fview%3Dnull%26uuid%3D72a93e228e5c4386a2a743091db6e5fd
        """
        base_url = 'https://graph.qq.com/oauth2.0/authorize?'
        params = {
            'response_type': 'code',
            'client_id': current_app.common.setting.get('QQ_APP_ID'),
            'redirect_uri': current_app.common.setting.get('QQ_REDIRECT_URL'),
            'state': current_app.common.setting.get('QQ_STATE'),
            'scope': 'get_user_info'  # 返回qq用户的openid
        }
        # urlencode 会把字典转换成url的查询字符串
        data = urlencode(params)
        url = base_url + data
        return {'url':url,'code':200}


class QQUserinfo(Resource):
    def code_value_(self,code):
        """根据返回的code 从qq 的token"""
        base_url = 'https://graph.qq.com/oauth2.0/token'
        if code:
            data = {
                'grant_type': "authorization_code",
                'client_id': current_app.config.get('QQ_APP_ID'),
                'client_secret': current_app.config.get("QQ_APP_KEY"),
                'code': code,
                'redirect_uri':current_app.config.get('QQ_REDIRECT_URL'),
            }
            # 发起请求
            resp = requests.request('GET',base_url, params=data)
            token_value = resp.text.split('&')[0][13:]
            return token_value

    def get_openid(self, token):
        """获取qq的openid"""
        base_url = "https://graph.qq.com/oauth2.0/me"
        data = {'access_token': token, "fmt": 'json'}
        # 根据access_token 获取扫码登录的用户信息
        resp = requests.request('GET', base_url, params=data)
        # 获取用户信息的openid, 扫码的用户信息
        user_dict = json.loads(resp.text)
        # openid 是扫码登录用户在qq 那边的用户id
        openid = user_dict['openid']
        return openid

    def get_qq_nickname(self, openid, token):
        """根据从qq获取的openid查询qq的昵称"""
        base_url = "https://graph.qq.com/user/get_user_info"
        data = {
            'oauth_consumer_key':current_app.config.get('QQ_APP_ID'),
            'access_token':token,
            'openid': openid
        }

        resp = requests.request('GET', base_url, params=data)
        print('用户信息的resp>>', resp.text)
        nick_name = json.loads(resp.text)['nickname']
        return nick_name

    def get(self):
        """根据token 获取openid"""
        parser = reqparse.RequestParser()
        parser.add_argument('code')
        args = parser.parse_args()
        code = args.get('code')
        print('code>>>>', code)
        # 获取access_token
        token_v = self.code_value_(code)
        print('token_v~~~~',token_v)
        openid = self.get_openid(token_v)
        return jsonify(msg="ok",code=200, data={'uid':openid})

    def post(self):
        """绑定账号信息"""
        parser = reqparse.RequestParser()
        parser.add_argument('username')
        parser.add_argument('password')
        parser.add_argument('unid')
        args = parser.parse_args()
        uname = args.get('username')
        pwd = args.get('password')
        openid = args.get('unid')
        # 判断账号是否注册过,没有注册过去注册
        print("?????",uname,pwd,openid)

        user = UserModels.query.filter_by(account=uname).first()
        if not user:
            return jsonify(msg="请先注册网站", code=400)
        # 校验密码
        try:
            check_password_hash(user.password, pwd)
        except Exception as e:
            return jsonify(msg="密码错误", code=400)
        # 根据user 查询oauthuser表中的数据, 绑定第三方账号
        oauth = OauthUser(image='', uid=openid, user=user.uid,oauth_type='qq')
        db.session.add(oauth)
        db.session.commit()
        # 返回绑定成功的用户token 及id
        token, refresh_token = _generate_token({'account': user.account, 'user_id': user.uid,
                                                'is_superuser': user.is_superuser})
        print('登陆的token', token)
        data = {
            'message': 'login success',
            'data': {'code': 200, 'token': token, 'refresh': refresh_token,
                     'account': user.account, 'uid': user.uid, }
        }
        return jsonify(msg='绑定成功',code=200, data=data )


api.add_resource(OauthUserr, '/qq_url')
api.add_resource(QQUserinfo,'/userinfo')




"""
1. 前端页面点击钉钉图片, 后端返回给用户一个扫码登录的页面
2. 用户扫码登录, 确认登录后,返回给用户一个:http://127.0.0.1:8080/dingding_back?code=b61cf0c1f5e73df298243c2ba4a9a62f&state=STATE
3. 前端要把url中code的值获取到传递后端, 后端根据code 的值获取钉钉账号的信息
4. 根据钉钉账号的信息,判断是否和后台中的账号是否绑定
    1. 绑定直接登录
    2.没有绑定, 返回给前端一个绑定账号的页面,
    3. 用户输入后台的账号信息,进行绑定
5. 返回绑定后的token, 用户信息
"""


class DingDingOauthResource(Resource):
    def get(self):
        base_url = 'https://oapi.dingtalk.com/connect/qrconnect?appid=%s&response_type=code&scope=snsapi_login&state=STATE&redirect_uri=%s'
        print(current_app.config.get('DING_REDIRECT_URI'),current_app.config.get('DING_APP_ID'))
        url = base_url % (current_app.config.get('DING_APP_ID'), current_app.config.get('DING_REDIRECT_URI'))
        # print('url>>',url)
        return {'url': url, 'code': 200}


class DingdingUserInfo(Resource):
    def get_ding_user(self, code):
        """获取登录的钉钉用户信息"""
        base_url = "https://oapi.dingtalk.com/sns/getuserinfo_bycode?signature="
        appid = current_app.config.get('DING_APP_ID')
        appSecret = current_app.config.get('DING_SECRET_KEY')
        t = time.time()
        # 把时间戳转换成毫秒
        timestamp = str(int(round(t*1000)))
        # 构造签名
        signature = base64.b64encode(
            hmac.new(appSecret.encode('utf-8'), timestamp.encode('utf-8'), digestmod=sha256).digest())
        params = {
            'timestamp':timestamp,
            'accessKey':appid,
            'signature': urllib.parse.quote(signature.decode('utf-8')),
        }
        # params 是查询字符串参数
        # data 是请求体参数
        # header 指明传递参数的类型
        # TODO 构造参数错误
        resp = requests.request('POST', base_url, params=params,
                                data=json.dumps({'tmp_auth_code':code}),
                                headers={'Content-Type': 'application/json'})
        print("ding的用户 resp>>>", resp)
        return resp.json()

    def get(self):
        """根据前端传来的code, 获取钉钉登录的用户信息"""
        parser = reqparse.RequestParser()
        parser.add_argument('code')
        args = parser.parse_args()
        code = args.get('code')
        print('code>>>>', code)

        # 根据code获取钉钉用户信息
        ding_user = self.get_ding_user(code)

        if ding_user['errcode'] != 0:
            return jsonify(msg="获取钉钉用户信息失败", code=500)
        # 获取钉钉的openid
        openid = ding_user['user_info']['openid']
        if openid:
            # 根据openid 判定是否绑定账号
            oauth_user = OauthUser.query.filter_by(uid=openid).first()
            if oauth_user:
                # 查询到用户,已经绑定过,
                user = UserModels.query.filter_by(uid=oauth_user.user).first()
                # 返回绑定成功的用户token 及id
                token, refresh_token = _generate_token({'account': user.account, 'user_id': user.uid,
                                                        'is_superuser': user.is_superuser})
                print('登陆的token', token)

                return jsonify(msg="登陆成功", data={'code': 200, 'token': token, 'refresh': refresh_token,
                                                 'account': user.account, 'uid': user.uid})
            else:
                return jsonify(msg="没有绑定用户,请先绑定", data={'uid': openid})

    def post(self):
        """绑定账号"""
        parser = reqparse.RequestParser()
        parser.add_argument('account')
        parser.add_argument('password')
        parser.add_argument('unid')
        args = parser.parse_args()
        uname = args.get('account')
        pwd = args.get('password')
        openid = args.get('unid')
        # 判断账号是否注册过,没有注册过去注册
        print("?????", uname, pwd, openid)

        user = UserModels.query.filter_by(account=uname).first()
        if not user:
            return jsonify(msg="请先注册网站", code=400)
        # 校验密码

        rest = check_password_hash(user.password, pwd)
        if not rest:
            return jsonify(msg="密码错误", code=400)
        # 根据user 查询oauthuser表中的数据, 绑定第三方账号
        oauth = OauthUser(image='', uid=openid, user=user.uid, oauth_type='qq')
        db.session.add(oauth)
        db.session.commit()
        # 返回绑定成功的用户token 及id
        token, refresh_token = _generate_token({'account': user.account, 'user_id': user.uid,
                                                'is_superuser': user.is_superuser})
        print('登陆的token', token)
        return jsonify(msg="绑定成功", code=200, data={'token': token, 'refresh': refresh_token,
                                                   'account': user.account, 'uid': user.uid})


api.add_resource(DingDingOauthResource, '/ding_url')
api.add_resource(DingdingUserInfo,'/user')
