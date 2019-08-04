# init_app.py


from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/keywords.sqlite3'
    app.config['SECRET_KEY'] = "random string"
    db.init_app(app)

    with app.app_context():
        import routes

        # creates only tables that do not exist
        db.create_all()
        db.session.commit()

        return app
