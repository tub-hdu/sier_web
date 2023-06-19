import random
import traceback
import logging
import redis
import json


from io import BytesIO
from flask import Blueprint, g, jsonify, request, make_response
from flask_restful import Api, Resource, marshal
from flask_restful.reqparse import RequestParser
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from datetime import datetime

from common.models import rds, db
from common.models.user_model import UserModels
from common.utils.smscode import send_message
from celery_tasks.task import phone_code
from common.utils.captcha import Captcha
from common.model_fields.user_fields import user_fields
from common.utils.mayjwt import _generate_token
# 创建蓝图
user_bp = Blueprint('user_bp', __name__, url_prefix='/user')

api = Api(user_bp)


class GenerateImgCode(Resource):
    """生成图片验证码"""
    def get(self):
        try:
            parser = RequestParser()
            parser.add_argument('uuid')
            args = parser.parse_args()
            uuid = args.get('uuid')
            # 生成图片验证码
            text, image = Captcha.gene_graph_captcha()
            # 保存验证码到redis
            rds.setex(uuid, 60 * 5, text)
            out = BytesIO()
            image.save(out, 'png')
            out.seek(0)
            resp = make_response(out.read())
            resp.content_type = 'image/png'
            return resp
        except:
            error = traceback.format_exc()
            logging.error('图片验证码 错误{}'.format(error))
            return 'fail'


# 注册
class Register(Resource):
    def post(self):
        """注册"""
        parse = RequestParser()
        parse.add_argument('username')
        parse.add_argument('password')
        parse.add_argument('password2')
        parse.add_argument('phone')
        parse.add_argument('code')
        # 校验
        args = parse.parse_args()
        name = args['username']
        mobile = args['phone']
        pwd = args['password']
        prd = args['password2']
        code = args['code']
        if not all([name, pwd, mobile, code, prd]):
            return jsonify({'message': '请完善信息','code': 400})
        # 验证码
        if code is None:
            return jsonify({'message': '请入如验证码', 'code': 400})
        if len(name) > 20:
            return jsonify({'message': '用户长度太长', 'code': 406})
        if len(pwd) > 20:
            return jsonify({'message': '密码长度不能太长', 'code': 406})
        # 密码
        if pwd != prd :
            return jsonify({"message": "两个密码不一致", 'code': 400})
        # 判断用户是否 唯一
        user = UserModels.query.filter_by(account=name, mobile=mobile).count()
        if user >= 1:
            return jsonify({'message': '用户已有或着手机重复了', 'code': 400})
        else:
            rdb = redis.Redis(host='localhost', port=6379, db=0)
            rdb_sms_code = rdb.get('sms_{}'.format(mobile))
            print("sadfa",rdb_sms_code)
            sms_code = rdb_sms_code.decode()
            print('asdfasd', sms_code)
            if sms_code != code:
                return jsonify({'message': '验证码不对', 'code': 400})
        user_info = UserModels(account=name, password=generate_password_hash(pwd), mobile=mobile)
        user_info.last_login_time = datetime.now()
        db.session.add(user_info)
        db.session.commit()
        return jsonify({'message': '注册成功', 'code': 200})


# 发送短信验证码
class SmsCode(Resource):
    """
        先写一个短信的配置（文件）
        短信验证码
        1点击前的发送的短信的按钮
        获取手机号
        2调用熔炼云的短信的配置写一个变量接受
        # 把json转换dict
        3判断发送的验证发statusCode == ‘000000’，和'112310'
        4然后写入redis里# setex(k,time,v)
        返回短信
    """
    def get(self):
        parse = RequestParser()
        parse.add_argument('phone')
        args = parse.parse_args()
        phone = args['phone']
        print(phone)
        resp, sms_code = phone_code(phone)
        print('......', sms_code)
        # 把json转换dict
        resp_data=json.loads(resp)
        if resp_data['statusCode'] == '112310' or resp_data['statusCode'] == '000000':
            # 1.发送成功的短信验证码，写入redis
            #2.TODO s使用那一种数据类型：hash set  zset string list
            # 3.用那一种存储短信验证码：string ：key phone value
            client=redis.Redis()
            # setex(k,time,v)
            client.setex('sms_{}'.format(phone),60000,str(sms_code))
            return jsonify({'message': '发送短信验证码成功', 'code': 200})
        else:
            return jsonify({'message': '发送短信验证码失败', 'code': 400})


# 登录
class Login(Resource):
    def post(self):
        """登录"""
        parse = RequestParser()
        parse.add_argument('account')
        parse.add_argument('password')
        parse.add_argument('uuid')
        parse.add_argument('img_code')
        args = parse.parse_args()
        uuid = args.get('uuid')
        img_code = args.get('img_code')
        name = args.get('account')
        pwd = args.get('password')

        print(">>>>>~~~~", name, pwd, uuid, img_code)
        # 校验图片验证码
        real_code = rds.get(uuid)
        if not real_code:
            return {'code': 407, 'message': '验证码过期'}
        real_code = real_code.decode()
        real_code = real_code.lower()
        code = img_code.lower()
        if real_code != code:
            return {'code': 406, 'message': '验证码错误'}

        user = UserModels.query.filter(or_(UserModels.account == name, UserModels.mobile == name)).first()
        print('当前登录的用户信息>>>', user)
        if not user:
            return {'msg': '账号或手机号错误', 'code': 400}
        if not check_password_hash(user.password, pwd):
            return {'code': 400, 'msg': '密码错误'}
        user_id = user.uid
        token, refresh_token = _generate_token(user.account, str(user.uid), user.is_superuser)
        print("打印token》》》", type(user.uid))
        data = {
            'message': 'login mucces',
            'data': {'user': user.username, 'token': token,  'code': 200, 'refresh': refresh_token,
                     'is_superuser': user.vid}
        }
        # 刷新生成tokenxW
        return jsonify(data)


class ChangePassWordRewsource(Resource):
    def put(self):
        """修改密码"""
        parser = RequestParser()
        args_list = ['pwd', 'phone', 'sms_code', 'confirm_pwd']
        for args in args_list:
            parser.add_argument(args)
        args = parser.parse_args()
        password = args.get('pwd')
        confirm_password = args.get('confirm_pwd')
        # 手机号
        phone = args.get('phone')
        # 手机验证码
        code = args.get('sms_code')
        # 密码长度
        if len(password) > 20:
            return {'message': '密码太长', 'code': 405}

        if password != confirm_password:
            return {'message': '两次密码不一致', 'code': 405}
        # 从redis中取出短信验证码
        real_msg_code = rds.get(phone)
        # 判断是否存在 不存在
        if not real_msg_code:
            return {'code': 405, 'message': '验证码已过期'}
        real_msg_code = real_msg_code.decode()
        print("redis_code.....", real_msg_code)
        print('code----->', code)
        # 进行验证是否一致
        if real_msg_code != code:
            return {'code': 405, 'message': '验证码错误'}
        # 对密码加密
        hash_pwd = generate_password_hash(password)
        # 修改密码
        try:
            UserModels.query.filter_by(mobile=phone).update({'password':hash_pwd})
            db.session.commit()
            return {'message':'修改密码成功', "code":200}
        except Exception as e:
            return {'message':'修改密码失败', 'code':500}

class UserInfoResource(Resource):
    def get(self):
        """获取用户信息"""
        parse = RequestParser()
        parse.add_argument('uid')
        args = parse.parse_args()
        user = UserModels.query.filter_by(uid=args.get('uid')).first()
        data = marshal(user, user_fields)
        return {'message':"获取用户信息成功", "data":data,"code":200}


# 注册路由
api.add_resource(Register, '/register_user')
# 图片验证码
api.add_resource(GenerateImgCode, '/generateimgcode')
# 校验验证码
api.add_resource(SmsCode, '/smscode')
# 登录
api.add_resource(Login, '/login')
# 修改密码
api.add_resource(ChangePassWordRewsource, '/change_pwd')