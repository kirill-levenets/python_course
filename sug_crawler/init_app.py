
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sug_config import DB_NAME, RANDOM_STRING, APP_NAME

db = SQLAlchemy()


def create_app():
    app = Flask(APP_NAME)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_NAME
    app.config['SECRET_KEY'] = RANDOM_STRING
    db.init_app(app)

    with app.app_context():
        import routes

        # creates only tables that do not exist
        db.create_all()
        db.session.commit()

        return app
