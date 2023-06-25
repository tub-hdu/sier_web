from flask import Blueprint
from flask_restful import Api,Resource


path_bp = Blueprint('path',__name__, url_prefix='/paths')
api = Api(path_bp)


class PathResource(Resource):
    def get(self):
        """
        获取所有的阶段路由

        """
        # TODO 查询所有的路径


api.add_resource(PathResource,'/get_path')