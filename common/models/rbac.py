from common.models import db

class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, nullable=True)
    # 与生成表结构无关，仅用于查询方便
    permission = db.relationship('Permission', secondary='roles_permission', backref='role')
    user = db.relationship('UserBase', secondary='user_roles', backref=db.backref('role'))

    def __repr__(self):
        return self.name


class UserRole(db.Model):
    """用户和角色的中间表"""
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id',ondelete="CASCADE"))
    user_id = db.Column(db.Integer, db.ForeignKey('tb_users.uid',ondelete="CASCADE"))


class Permission(db.Model):
    """权限表"""
    __tablename__ = 'permission'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True, nullable=False, doc='权限名称')


class RoleAndPermission(db.Model):
    __tablename__ = 'roles_permission'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id',ondelete="CASCADE"))
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id',ondelete="CASCADE"))


class Path(db.Model):
    """路径表"""
    __tablename__ = 'path'
    id =  db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(32),  nullable=True, doc='路由的名字')
    img = db.Column(db.String(256), nullable=True, doc='路径图片')
    desc = db.Column(db.String(256), nullable=True, doc='路径描述')
    permission = db.relationship('Permission', secondary='permission_path', backref='per')
    jieduan = db.Column(db.Integer, db.ForeignKey('jieduan.id',ondelete='CASCADE'),doc='阶段')


class PermissionAndPath(db.Model):
    """权限和路径"""
    __tablename__ = 'permission_path'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id', ondelete="CASCADE"))
    path_id = db.Column(db.Integer, db.ForeignKey('path.id', ondelete="CASCADE"))


class JieDuan(db.Model):
    """阶段表"""
    __tablename__ = 'jieduan'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sequence = db.Column(db.Integer, doc='阶段的序号')
    name = db.Column(db.String(32),  nullable=True, doc='阶段名字')
    path = db.relationship('Path', backref='jieduan', doc='路径')
    courses = db.relationship('Course', backref='jieduan', doc='课程')