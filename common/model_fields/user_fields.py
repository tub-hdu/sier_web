from flask_restful import fields


user_fields = {
    'uid': fields.Integer,
    'account': fields.String,
    'mobile': fields.String,
    'uname': fields.String,
    'email': fields.String,
    'profile_photo': fields.String,
    'is_superuser': fields.Integer
}

vip_fields = {
    'level':fields.Integer,
    'price':fields.String,
    'vip_cour':fields.Integer,
    'exempt_cour':fields.Integer,
    'save':fields.Integer,
    'environment': fields.Integer,
    'client':fields.Integer,
    'ssh':fields.Integer,
    "web_ide":fields.Integer,
    'discounts':fields.Integer,
    'exempt_study':fields.Integer
}