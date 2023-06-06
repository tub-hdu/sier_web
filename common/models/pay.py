from common.models import db

class Orders(db.Model):
    """
    订单表
    """
    __tablename__ = 'tb_order'
    user = db.Column(db.Integer, db.ForeignKey("tb_users.uid", ondelete="CASCADE"), doc='下单用户')
    vip = db.Column(db.Integer, db.ForeignKey("vip.id", ondelete="CASCADE"))
    order_id = db.Column(db.String(24), doc='订单号（自己生成）', primary_key=True)
    trade_no = db.Column(db.String(512), doc='支付宝订单号')
    pay_time = db.Column(db.DateTime)
    pay_method = db.Column(db.String(24), doc='支付方式', default='支付宝')
    status = db.Column(db.Integer, doc='0未支付1已支付2取消支付3支付异常', default=0)
    total_amount = db.Column(db.DECIMAL(20, 5), doc='商品总金额')
    cur_amount = db.Column(db.DECIMAL(20, 5), doc='折扣后的价格')
    pay_amount = db.Column(db.DECIMAL(20, 5), doc='实际支付金额')
    record = db.Column(db.String(256), doc='支付信息')

    def __str__(self):
        return self.order_id