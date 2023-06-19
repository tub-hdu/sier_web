import json
from flask import Blueprint,jsonify
from flask_restful import Api,Resource,marshal
from common.models.user_model import Vip
from common.model_fields.user_fields import vip_fields

vip_bp = Blueprint('vip',__name__, url_prefix='/vip')
api = Api(vip_bp)


class VipResource(Resource):
    def get(self):
        """获取所有的vip"""
        vips_info = Vip.query.all()
        # print('vips-->',vips_info)
        result = {}
        for vip in vips_info:
            if vip.level == 0:
                # 免费用户
                common_user_list = json.loads(json.dumps(marshal(vip, vip_fields)))
                # print("用户信息等级>>>", common_user_list)
                common_user_list['level']='免费'
                # print("用户信息等级112>>>", common_user_list)
                result['common_list'] = common_user_list
            if vip.level == 1:
                common_vip_list = json.loads(json.dumps(marshal(vip, vip_fields)))
                common_vip_list['level']='普通会员'
                result['common_vip_list'] = common_vip_list
            if vip.level == 2:
                expert_vip_list = json.loads(json.dumps(marshal(vip, vip_fields)))
                expert_vip_list['level']='高级会员'
                result['expert_vip_list'] = expert_vip_list

        return jsonify(message='ok',code=200, data=result)

api.add_resource(VipResource,'/get_vip_list')