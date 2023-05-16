import time
import logging
import traceback

from ronglian_sms_sdk import SmsSDK

from celery_tasks import celery_app

accId = '8aaf07087e7b9872017f20bfea591acf'
accToken = 'cebd18474df5466a8eec2cc824004135'
appId = '8aaf07087e7b9872017f20bfeb5e1ad6'


# @app.task 指定将这个函数的执行交给celery异步执行
@celery_app.task
def test(mobile, code):
    print('1111')
    time.sleep(15)
    return mobile + code


@celery_app.task
def phone_code(mobile, code):
    logging.info('phone_code:{}'.format(locals()))
    resp = 0
    try:
        sdk = SmsSDK(accId, accToken, appId)
        datas = (code, '5')
        resp = sdk.sendMessage('1', mobile, datas)
    except:
        error = traceback.format_exc()
        logging.error('phone_code error:{}'.format(error))
    return resp