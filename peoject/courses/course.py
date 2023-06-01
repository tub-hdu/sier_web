import json
import traceback
from flask import Blueprint,jsonify
from sqlalchemy import and_,or_
from flask_restful import Api,Resource,marshal,reqparse

from common.models.course import Tag,Course,CourseTag,CourseType, Sections
from common.model_fields.course_fields import tag_fields, course_fields, chapter_fields, sections_fields, comment_fields
from common.utils.login_util import login_required
from common.es.create_es_index import Elasticsearch


course_bp = Blueprint('course',__name__, url_prefix='/course')

api = Api(course_bp)


class TagsResource(Resource):
    def get(self):
        """获取全部的标签"""
        try:
            tags = Tag.query.all()
            data = marshal(tags, tag_fields)
            return jsonify(mesage="标签获取成功", data=data)
        except Exception as e:
            print(e)
            return jsonify(message="标签获取失败",code=500)


class CourseResource(Resource):
    def get(self):
        """获取所有的课程"""
        parser = reqparse.RequestParser()
        params = ['page','size','tag_id','free', 'online','sort']
        for data in params:
            parser.add_argument(data)
        args = parser.parse_args()
        tag_id = args.get('tag_id')
        free = args.get('free')
        online = args.get('online')
        sort = args.get('sort')
        print("tag_id的值%s, online的值%s, free的值%s,sort的值%s"%(tag_id, online, free, sort))

        # 2.若有的参数有值,有的参数没有值, 是根据参数值进行过滤查询
        if tag_id:
            print("标签有值",tag_id)
            tag = Tag.query.filter_by(id=int(tag_id)).first()
            # 若标签有值
            # 获取标签
            if free == "" and online == '':
                course_tag = Tag.query.filter_by(id=int(tag_id)).first()
                # 获取所标签下的所有的值
                courses = course_tag.course
                course_data = marshal(courses, course_fields)

            if free != '' and online == '':
                # free是免费的限免会员
                print("free", free)
                course_type = CourseType.query.filter_by(title=free).first()
                # 根据类型获取, 然后再根据tag_id 过滤
                course_data = marshal(course_type.course, course_fields)

            if free != '' and online != '':
                course_type = CourseType.query.filter_by(title=free).first()
                if online == '1':
                    online_v= '已上线'
                else:
                    online_v='即将上线'
                print(online_v, type(online))
                courses = Course.query.filter(and_(Course.course_type == course_type.id, Course.status == online_v)).all()
                course_data = marshal(courses, course_fields)
            # 根据tag_id 过滤
            filter_course = json.loads(json.dumps(course_data))
            print("_____>", filter_course)
            for course in filter_course:
                if course['id'] != tag.id:
                    filter_course.remove(course)
            return filter_course

        else:
            # 标签没有值
            # print(json.loads(json.dumps(course_list)))
            # 全部为空, 查询全部数据
            if sort == "" and tag_id == "" and online == "" and free == "":
                course_list = Course.query.all()
                course_data = marshal(course_list, course_fields)
                return jsonify(message='ok', code=200, data=course_data)
            if free != "" and online == '':
                course_type = CourseType.query.filter_by(title=free).first()
                course_data = marshal(course_type.course, course_fields)
                print("_____>", course_data)
                return course_data
            if online != ''  and free == '':
                if online == '1':
                    online_v = '已上线'
                else:
                    online_v = '即将上线'
                courses = Course.query.filter_by(status=online_v).all()
                course_data = marshal(courses, course_fields)
                return course_data
            if online != ''  and free != '':
                course_type = CourseType.query.filter_by(title=free).first()
                if online == '1':
                    online_v= '已上线'
                else:
                    online_v='即将上线'
                courses = Course.query.filter(and_(Course.course_type == course_type.id, Course.status==online_v)).all()
                course_data = marshal(courses, course_fields)
                return course_data


class CourseInfoResource(Resource):
    def get(self):
        """
        获取课程详情
        判断token
        """
        parser = reqparse.RequestParser()
        parser.add_argument('cid')
        args = parser.parse_args()
        # 根据cid 获取课程
        cid = args.get('cid')
        print('cid>>>', cid)
        course = Course.query.filter_by(id=cid).first()
        print('ciurse>>', course)
        # 根据课程获取章节信息
        chapter_list = course.chapters
        print('list--->', chapter_list)
        # 课程下的所有章节
        # chapters = json.loads(json.dumps(marshal(chapter_list, chapter_fields)))
        # print('chapter_list---->', chapters)
        # # TODO 根据每个章节获取每个小节
        course_data = {}
        chapter_data = []
        for chapter in chapter_list:
            course_data = {
                'id': chapter.id,
                'title': course.title,
                'serial_num': chapter.serial_num,
                'course': chapter.course,
                'collect_num': course.follower
                # 'sections': chapter.sections
            }
            chapter_data.append({
                'id': chapter.id,
                'title': chapter.title,
                'sections': json.dumps(marshal(chapter.sections, sections_fields))
            })

        result = {
            'course_ser': course_data,
            'section_ser': chapter_data
        }
        return {'message': 'ok', "data": result}


class VideoInfoResource(Resource):

    @login_required
    def get(self):
        """根据小节id 获取视频播放地址"""
        parser = reqparse.RequestParser()
        parser.add_argument('sid')
        args = parser.parse_args()
        sid = args.get('sid')
        section = Sections.query.filter_by(id=sid).first()
        video_url = section.video

        return jsonify(mesage='ok', url=video_url)


class CourseSearch(Resource):
    def get(self):
        """搜索"""
        parser = reqparse.RequestParser()
        parser.add_argument('q')
        args = parser.parse_args()
        key_word = args.get('q')
        # 从es 中查询
        es = Elasticsearch(hosts='http://localhost:9200')
        # 返回查询的结果
        rest = es.search(query=key_word)
        return rest


api.add_resource(TagsResource,'/get_tag')
api.add_resource(CourseResource,'/get_course')
api.add_resource(CourseInfoResource, '/courseinfo')
api.add_resource(VideoInfoResource,'/sectionvideo')
# 搜索
api.add_resource(CourseSearch, '/gettag')