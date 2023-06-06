from common.models import db
from datetime import datetime


class Base(db.Model):
    """
    基础表
    """
    __abstract__ = True
    create_time = db.Column(db.DateTime, default=datetime.now, doc='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now, doc='更新时间')
    user_id = db.Column(db.Integer, doc='课程相关添加人')
    is_delete = db.Column(db.Boolean, default=False, doc='当时数据是否删除')