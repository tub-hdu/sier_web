import logging
import string
import random
import time
import traceback
import random
import redis
from ronglian_sms_sdk import SmsSDK
from qiniu import Auth


from common.models.user_model import UserModels

# 容联
from common.utils.captcha import Captcha

accId = '8aaf07087e7b9872017f20bfea591acf'
accToken = 'cebd18474df5466a8eec2cc824004135'
appId = '8aaf07087e7b9872017f20bfeb5e1ad6'
# 七牛
# 需要填写你的 Access Key 和 Secret Key
access_key = 'otmSGYDq9n7k0oc94-Pf08epGvi--5mvXvOduMsZ'
secret_key = 'xeYWDWr3kAGGKcVbJYS07HDSPYUp1qkbAYZcbUk9'


def send_message(mobile):
    sdk = SmsSDK(accId, accToken, appId)
    # 短信验证码模板
    tid = '1'
    # 随机生成验证码
    data = random.randint(100000, 999999)
    datas = (data,)

    print("生成的短信验证码>>>>>",datas)
    resp = sdk.sendMessage(tid, mobile, datas)
    print("验证码的内容",resp)
    rdb= redis.Redis(host='localhost',port=6379,db=0)
    rdb.setex("sms_%s" % mobile, 300,datas[0])
    rdb.close()
    return resp, data


def generate_code():

    return Captcha.gene_graph_captcha()


def random_string_generator(str_size):
    allowed_chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(allowed_chars) for x in range(str_size))


def get_upload_token():
    """
    获取上传文件的token
    :return:
    """
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = 'courses1'
    # 上传后保存的文件名
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, 3600)
    return token


def check_is_manager(user_id):
    """
    检查用户是否为管理员
    :return:
    """
    user = UserModels.query.get(user_id)
    # 判断该用户有没有添加的权限
    if user.is_superuser == 0:
        return False
    return True