from flask import Flask
from flask_cors import CORS

from common.models import db
from peoject.logs.user import user_bp
from peoject.logs.oauth_user import oauth_user_bp
from peoject.courses.course import course_bp
from peoject.courses.comment import comment_bp
from peoject.logs.vip import vip_bp
from peoject.courses.pay.pay import pay_bp


def create_flask_app(config):
    app = Flask(__name__)
    # 配置文件
    app.config.from_object(config)

    # 初始化整个项目的db
    db.init_app(app)

    # 注册蓝图
    app.register_blueprint(user_bp)
    app.register_blueprint(oauth_user_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(vip_bp)
    app.register_blueprint(pay_bp)
    # 对所有的请求进行跨域
    cors = CORS(app)
    return app
