from flask import Blueprint, request
from flask_restful import Resource, Api, reqparse

from common.models import db
from common.utils.login_util import login_required
from common.models.rbac import Permission


rbac_bp = Blueprint('rbac_bp', __name__, url_prefix='/rbacs')
api = Api(rbac_bp)


class AddPermission(Resource):
    """添加权限"""
    @login_required
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('name')
        args = parse.parse_args()
        name = args.get('name')
        if not all([name]):
            return {'msg': "请补全权限"}
        if len(name) > 30:
            return {'msg': '名字过长', 'code': 500}
        num = Permission.query.filter_by(name=name).first()
        if num:
            return {"msg": '名字已存在,不能进行添加', 'code': 500}
        roles = Permission(name=name)
        db.session.add(roles)
        db.session.commit()
        return {'msg': '添加成功', 'code': 200}


class GetPermission(Resource):
    """获取权限"""
    def get(self, id):
        per = Permission.query.filter_by(id=id).all()
        if per:
            return {'msg': '该数据存在，获取成功', 'code': 200}
        else:
            return {'msg': '该数据不存在，获取失败', 'code': 400}


class UpdatePermission(Resource):
    """修改权限"""
    @login_required
    def put(self, id):
        parse = reqparse.RequestParser()
        parse.add_argument('name')
        args = parse.parse_args()
        name = args.get('name')
        if not all([name]):
            return {'msg': "请补全权限"}
        if len(name) > 30:
            return {'msg': '名字过长', 'code': 400}
        perssions_1 = Permission.query.filter_by(id=id).first()
        if not perssions_1:
            return {'msg': '该数据不存在,不能进行修改'}
        Permission.query.filter_by(id=id).update({"name": name})
        db.session.commit()
        return {'msg': '修改成功', 'code': 200}


class DeletePermission(Resource):
    """删除权限"""
    @login_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id')
        args = parse.parse_args()
        id = args.get('id')
        per = Permission.query.filter_by(id=id).first()
        if per:
            per.session.delete(per)
            db.session.commit()
            return {'msg': '该数据存在，删除成功', 'code': 200}
        else:
            return {'msg': '该数据不存，在删除失败', 'code': 400}


# 添加权限
api.add_resource(AddPermission, '/add_per')
# 获取权限
api.add_resource(GetPermission, '/get_per/<int:id>')
# 修改权限
api.add_resource(UpdatePermission, '/update_per/<int:id>')
# 删除权限
api.add_resource(DeletePermission, '/delete_per')