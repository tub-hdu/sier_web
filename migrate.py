from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from main import app
from common.models import db
from common.models.user_model import *
from common.models.base import *
from common.models.course import *
from common.models.pay import *
from common.models.rbac import *

manage = Manager(app)
migrate = Migrate(app, db)
manage.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manage.run()