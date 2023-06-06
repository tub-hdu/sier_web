import datetime
from common.models import db


class UserModels(db.Model):
    """用户模型类"""
    __tablename__ = 'tb_users'

    uid = db.Column(db.Integer, primary_key=True, autoincrement=True,doc="用户id")
    account = db.Column(db.String(32), unique=True, doc='账号')
    uname = db.Column(db.String(32), doc='昵称')
    password = db.Column(db.String(256), doc="密码")
    mobile = db.Column(db.String(11), unique=True, doc='手机号')
    email = db.Column(db.String(32), doc='邮箱')
    profile_photo = db.Column(db.String(256), doc='头像',nullable=True)
    is_superuser = db.Column(db.Integer, default=0,doc="0普通用户1会员2高级会员")
    create_time = db.Column(db.DateTime, default=datetime.datetime.now())
    last_login_time = db.Column(db.DateTime, nullable=True, doc="最后登录时间")
    vip_expiration = db.Column(db.DateTime, nullable=True,doc='vip到期时间')
    vip = db.Column(db.Integer, db.ForeignKey('vip.id', ondelete="CASCADE"),doc="vip表")

    comment = db.relationship('Comment',backref='tb_user')

class Vip(db.Model):
    """会员用户"""
    __tablename__ = 'vip'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), doc='vip名称')
    level = db.Column(db.Integer, doc='vip等级(普通会员,高级会员)')
    price = db.Column(db.DECIMAL(20, 2), doc='会员价格')
    desc = db.Column(db.String(64), doc='vip描述')
    period = db.Column(db.Integer, default=365, doc='vip有效期')
    exempt_cour = db.Column(db.Integer, doc='免费课程{0或空:不享受,1:享受}')
    vip_cour = db.Column(db.Integer, doc='会员课程{0或空:不享受,1:享受}')
    environment = db.Column(db.Integer, doc='实验环境联网{0或空:不享受,1:享受}')
    save = db.Column(db.Integer, doc='保存2个环境(30天){0或空:不享受,1:享受}')
    client = db.Column(db.Integer, doc='客户端{0或空:不享受,1:享受}')
    ssh = db.Column(db.Integer, doc='SSH直连{0或空:不享受,1:享受}')
    web_ide = db.Column(db.Integer, doc='WebIDE {0或空:不享受,1:享受}')
    discounts = db.Column(db.Integer, doc='训练营优惠{0或空:不享受,1:享受}')
    exempt_study = db.Column(db.Integer, doc='训练营课程免费学习{0或空:不享受,1:享受}')


class OauthUser(db.Model):
    """
    第三方登录表(微信登录/qq登录/微博登录)
    """
    __tablename__ = 'oauth_user'
    id = db.Column(db.Integer, primary_key=True, doc='oauth_user id')
    image = db.Column(db.String(64), doc='头像')
    uid = db.Column(db.String(512), doc='第三方登录的id')
    user = db.Column(db.Integer, db.ForeignKey("tb_users.uid", ondelete="CASCADE"))
    oauth_type = db.Column(db.String(128), doc='第三方登录类型')

    @classmethod
    def is_bind_user(cls, uid, oauth_type):
        """
        是否绑定用户
        """
        oauth = OauthUser.query.filter_by(uid=uid, oauth_type=oauth_type).first()
        if oauth:
            return True
        return False