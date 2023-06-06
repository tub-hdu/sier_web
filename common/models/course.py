import datetime

from common.models import db
from common.models.base import Base


class CourseType(Base):
    """
    课程类别
    """
    __tablename__ = 'tb_course_type'
    id = db.Column(db.Integer, primary_key=True, doc='课程类型id')
    title = db.Column(db.String(16), doc='课程类别')
    sequence = db.Column(db.Integer, doc='展示顺序', default=10)
    course = db.relationship('Course', backref='type')

    def __str__(self):
        return self.title


class Tag(Base):
    """
    课程标签
    """
    __tablename__ = 'tb_course_tag'

    id = db.Column(db.Integer, primary_key=True, doc='课程标签id')
    title = db.Column(db.String(16), doc='课程类别')
    sequence = db.Column(db.Integer, doc='展示顺序', default=10)
    # 多对多关系
    course = db.relationship('Course', secondary='course_tag', backref=db.backref('tags'))

    def __str__(self):
        return self.title


class Course(Base):
    """
    课程表
    """
    __tablename__ = 'tb_course'
    STATUS = (
        ('0', '即将上线'),
        ('1', '已上线'),
        ('2', '已下线'),
    )
    id = db.Column(db.Integer, primary_key=True, doc='课程id')
    title = db.Column(db.String(24), doc='课程名称')
    desc = db.Column(db.String(256), doc='课程描述')
    img_path = db.Column(db.String(256), doc='课程logo地址')
    course_type = db.Column(db.Integer, db.ForeignKey("tb_course_type.id", ondelete="CASCADE"))
    status = db.Column(db.String(8), doc='课程logo地址', default='已上线')
    follower = db.Column(db.Integer, default=0, doc='关注人数')
    learner = db.Column(db.Integer, default=0, doc='学习人数')
    chapters = db.relationship('Chapters', backref='tb_course')

    comments = db.relationship('Comment', backref='tb_course')
    jieduan = db.Column(db.Integer, db.ForeignKey('jieduan.id',ondelete='CASCADE'),doc='阶段')


class CourseTag(Base):
    """
    中间表  课程、标签的中间表
    """
    __tablename__ = 'course_tag'
    course_id = db.Column(db.Integer, db.ForeignKey("tb_course.id"), primary_key=True, doc='课程id')
    tag_id = db.Column(db.Integer, db.ForeignKey("tb_course_tag.id"), primary_key=True, doc='标签id')
    is_delete = db.Column(db.Boolean, doc='状态(0存在对应关系;1不存在对应关系)')


class Chapters(Base):
    """
    章节目录
    """
    __tablename__ = 'tb_chapters'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(24), doc='章标题')
    serial_num = db.Column(db.Integer, doc='章序号')
    course = db.Column(db.Integer, db.ForeignKey("tb_course.id", ondelete="CASCADE"), doc='课程')
    sections = db.relationship('Sections', backref='tb_chapters')

    def __str__(self):
        return self.title


class Sections(Base):
    """
    小节表
    """
    __tablename__ = 'tb_sections'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(24), doc='章标题')
    serial_num = db.Column(db.Integer, doc='章序号')
    chapters = db.Column(db.Integer, db.ForeignKey("tb_chapters.id", ondelete="CASCADE"), doc='课程')
    learn_time = db.Column(db.Integer, doc='学习小时', default=1)
    content = db.Column(db.Text, doc='学习内容')
    video = db.Column(db.String(256), doc='学习视频')
    seq_num = db.Column(db.Integer, doc='序号', default=1)
    like_count = db.Column(db.Integer, doc='点赞次数', default=0)

    def __str__(self):
        return self.title


class Comment(db.Model):
    '''评论'''
    """
    能评论课程
    能对课程的评论进行回复
    """
    __tablename__ = 'tb_comment'
    cid = db.Column(db.Integer, primary_key=True, autoincrement=True, doc='评论的id')
    course = db.Column(db.Integer, db.ForeignKey('tb_course.id', ondelete="CASCADE"),doc='课程')
    user = db.Column(db.Integer, db.ForeignKey('tb_users.uid', ondelete="CASCADE"),doc='用户')
    parent_id = db.Column(db.Integer, db.ForeignKey('tb_comment.cid',ondelete="CASCADE"), nullable=True,doc='被评论的id')
    content = db.Column(db.Text, doc='评论内容')
    created_time = db.Column(db.DateTime, default=datetime.datetime.now(), doc='评论时间')
    to_user = db.Column(db.Integer, db.ForeignKey('tb_users.uid', ondelete="CASCADE"), nullable=True,doc='回复评论的用户')
    like_count = db.Column(db.Integer, default=0, doc='点赞数')
    reply_count = db.Column(db.Integer, default=0, doc='回复数')
    is_top = db.Column(db.Boolean, default=False, doc='是否置顶')
    status = db.Column(db.Integer, default=1, doc='评论状态')
