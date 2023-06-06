from flask_sqlalchemy import SQLAlchemy
from common.setting.default import Redis

db = SQLAlchemy()
rds = Redis().connect()