from flask import Flask
from database import db

from routes import add_routes


def create_app(database_uri):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    add_routes(app)

    db.init_app(app)
    db.create_all(app=app)

    return app


app = Flask(__name__)


if __name__ == '__main__':
    import configparser

    config = configparser.ConfigParser()
    config.read('alembic.ini')
    app = create_app(config['alembic']['sqlalchemy.url'])

    app.run()