from flask import Flask
from flask.ext.script import Manager


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('settings.py')
    return app


def create_manager(app):
    manager = Manager(app)
    return manager
