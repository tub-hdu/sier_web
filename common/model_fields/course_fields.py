from flask_restful import fields

tag_fields = {
    'id':fields.Integer,
    'title':fields.String,
    'sequence': fields.Integer
}


course_fields = {
    'id':fields.Integer,
    'title': fields.String,
    'img_path': fields.String,
    'status': fields.String,
    'follower': fields.Integer,
    'learner': fields.Integer,
    'course_type':fields.Integer
}

chapter_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'ser_num': fields.Integer,
}
sections_fields = {
    'id':fields.Integer,
    'title': fields.String,
    'serial_num': fields.Integer,
    'learn_time': fields.Integer,
    'content':fields.String,
    'video': fields.String,
    'seq_num':fields.Integer,
    'like_count': fields.Integer
}

comment_fields = {
    "cid": fields.Integer,
    'content':fields.String,
    'created_time': fields.DateTime,
    'like_count':fields.Integer,
    'reply_count': fields.Integer,
    'user':fields.Integer,
    'to_user':fields.Integer,
    'parent_id': fields.Integer,
    'course': fields.Integer
}