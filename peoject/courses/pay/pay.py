import logging
import datetime
import random
from flask import Blueprint,g
from flask_restful import Api,Resource,reqparse
from alipay import AliPay
from common.utils.login_util import login_required
from common.utils.custom_resp_json import custom_json
from common.models.pay import Orders
from common.models import db

pay_bp = Blueprint('pay',__name__, url_prefix='/pay')

api = Api(pay_bp)


# 使用representation把所有返回的数据进行统一化
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = custom_json(data, code, headers)
    return resp


class OrderCreateResource(Resource):

    @login_required
    def get(self):
        """
        创建订单号
        """
        order = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + \
                str(g.user_id) + str(random.randint(100000,999999))

        return {'order':order}


class AlipayResource(Resource):
    def __init__(self):
        self.app_private_key_string = open('syl_project/pay/app_private_key.pem').read()
        self.alipay_public_key_string = open('syl_project/pay/alipay_public_key.pem').read()

        self.alipay_getway = 'https://openapi.alipaydev.com/gateway.do'
        self.alipay_obj = self.get_alipay_obj()

    def get_alipay_obj(self):
        alipay_obj = AliPay(
            appid="2016091400513191",  # 沙箱appid
            app_notify_url="http://127.0.0.1:8080/callback",  # 默认回调url
            app_private_key_string=self.app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=self.alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True,  # 默认False,我们是沙箱，所以改成True(让访问沙箱环境支付宝地址)
        )
        return alipay_obj

    @login_required
    def get(self):
        """
        扫码登录的url
        :return:  返回一个用户登录的扫码登录的url
        """
        parser = reqparse.RequestParser()
        parser.add_argument('order')
        parser.add_argument('price')
        parser.add_argument('record')
        args = parser.parse_args()
        order_id = args.get('order')
        price = args.get('price')

        order_str = self.alipay_obj.api_alipay_trade_page_pay(
            subject="实验楼消费",
            out_trade_no="%s" % order_id,  # 订单号  注意，标准的json格式没有 '' 单引号，只有 "" 双引号，python默认为 '' 单引号
            total_amount=price,  # 订单价格
        )
        alipay_url = self.alipay_getway + "?" + order_str
        print('url---->', alipay_url)
        return {'message':'请求成功，跳转支付页面','code':200, "data":alipay_url}

    @login_required
    def post(self):
        """创建订单"""
        parser = reqparse.RequestParser()
        parser.add_argument('order')
        parser.add_argument('price')
        parser.add_argument('record')
        args = parser.parse_args()
        order_id = args.get('order')
        price = args.get('price')
        record = args.get('record')
        user_id = g.user_id
        # TODO  创建订单失败要回滚
        try:
            # 创建订单信息
            order = Orders(
                user=user_id,
                vip= record,
                order_id=order_id,
                pay_amount=price,
                pay_time = datetime.datetime.now()
            )
            db.session.add(order)
            db.session.commit()
            return {'message':'创建订单成功',"code":200}
        except Exception as e:
            logging.error("create order error, reason is %s"% e)
            return {'message':"创建订单失败","code":500}


class AliPayCallback(Resource):

    @login_required
    def post(self):
        """获取支付成功的标识,写入数据库, 创建订单"""
        parser = reqparse.RequestParser()
        parser.add_argument('trade_no')
        parser.add_argument('order_id')
        parser.add_argument('timestamp')
        parser.add_argument('pay_amount')
        args = parser.parse_args()
        trade_no = args.get('trade_no')

        order_id = args.get('order_id')

        # 获取token中的uid
        user_id = g.user_id
        order = Orders.query.get(order_id=order_id)
        if not order:
            return {"code": 500, "message": "购买失败"}
        # 对比订单是否和前端传来的是否一样, 一样说明支付成功
        order.trade_no = trade_no

        # 修改订单的状态
        order.status = 1
        db.session.commit()
        return {"code": 200, "message": "购买成功"}

api.add_resource(OrderCreateResource,'/create_order')
api.add_resource(AlipayResource,'/alipay')
api.add_resource(AliPayCallback,'/alipay_callback')