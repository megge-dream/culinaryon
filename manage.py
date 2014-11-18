#!/usr/bin/env python

from flask.ext.script import Manager, Server
from flask.ext.script.commands import ShowUrls, Clean

from app.api import app, db
from app.api.users.model import User


manager = Manager(app)
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())
manager.add_command("server", Server())


@manager.shell
def make_shell_context():
    """ Creates a python REPL with several default imports
        in the context of the app
    """

    return dict(app=app, db=db, User=User)


@manager.command
def syncdb():
    """ Creates a database with all of the tables defined in
        your Alchemy models
    """

    db.drop_all()
    db.create_all()


if __name__ == '__main__':
    manager.run()