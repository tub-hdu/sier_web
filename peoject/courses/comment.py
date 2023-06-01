from copy import deepcopy
from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, fields, current_app, marshal_with

from common.models import db
from common.models.course import Course, Comment
from common.models.user_model import UserModels
from common.model_fields.comment_fields import comment_fields
from common.utils.custom_output_json import custom_output_json
from common.utils.login_util import login_required, superuser


comment_bp = Blueprint('comment_bp', __name__, url_prefix='/common')
api = Api(comment_bp)


class AddComment(Resource):
    """
    添加评论
    1、获取用户id、课程id、评论内容
    2、检查课程是否存在
    3、添加评论
    """
    @login_required
    @superuser
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('course_id')
        parser.add_argument('content')
        args = parser.parse_args()
        course_id = args.get('course_id')
        content = args.get('content')
        if not all([content,course_id]):
            return {"msg": '评论信息不全'}, 400
        course = Course.query.get(course_id)
        if not course:
            return {"msg": '没有该课程'}, 400
        comment = Comment(course=course_id, content=content)
        db.session.add(comment)
        db.session.commit()
        return {'评论添加成功'},200


class UpComment(Resource):
    """
        修改评论
    """
    @login_required
    def put(self):
        # 获取校验的参数
        re = reqparse.RequestParser()
        re.add_argument("id")
        args = re.parse_args()
        id = args.get("id")
        comment = Comment.query.filter_by(id=id).first()
        if not comment:
            return {"message": "没有该评论", "code": 500}
        if comment.status == 1:
            return {"message": "评论违规", "code": 500}
        comment.status = 1
        db.session.commit()
        return {"message": "ok", "code": 200}


class GetComments(Resource):
    """
    获取评论
    """
    def get(self):
        res = {}
        parse = reqparse.RequestParser()
        parse.add_argument("course_id")
        args = parse.parse_args()
        course_id = args.get("course_id")
        # 获取评论
        comments = Comment.query.filter_by(course=course_id).all()

        comment_list = marshal(comments, comment_fields)
        result = []
        for comment in comment_list:
            comment.update({
                'childlist': [],
                'user_info': {
                    'username': '1'
                },
                'is_favorite': 0,
                'count': 10
            })
            list1 = deepcopy(comment)
            list1 = [list1]
            comment.update({
                'childlist': list1
            })
            result.append(comment)

        return result


# 添加评论
api.add_resource(UpComment, '/update_comment')
# 修改评论
api.add_resource(AddComment, '/add_comment')
# 获取评论
api.add_resource(GetComments, '/get_comment')