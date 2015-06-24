# -*- coding: utf-8 -*-
from flask.ext.migrate import Migrate, MigrateCommand
from app.api import app, db
from manage import manager

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()