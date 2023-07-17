from flask_restful import fields

comment_fields = {
    "id": fields.Integer,
    "uid": fields.Integer(attribute='user'),
    "course": fields.Integer,
    "create_time": fields.DateTime,
    "update_time": fields.DateTime,
    "content": fields.String
}