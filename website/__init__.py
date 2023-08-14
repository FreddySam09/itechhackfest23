from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from datetime import datetime, timedelta
from flask import session
import logging
from flask import Flask

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    log_file = 'app.log'  # Name of the log file

    logging.basicConfig(filename=log_file, level=logging.INFO, format=log_format)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Slot  # Update the import here

    with app.app_context():
        db.create_all()
        populate_systems()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

from .models import System

def create_database(app):
    from .models import Slot

    with app.app_context():  # Enter application context
        if not path.exists('website/' + DB_NAME):
            db.create_all()
            print('Created Database!')

            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            for day in range(7):
                start_time = today + timedelta(days=day, hours=9)  # 9 AM
                for _ in range(4):
                    new_slot = Slot(start_time=start_time, end_time=start_time + timedelta(hours=2),)
                    db.session.add(new_slot)
                    start_time += timedelta(hours=3)  # Move to the next time interval

            db.session.commit()


def populate_systems():
    system_names = ["System 1", "System 2", "System 3", "System 4", "System 5"]

    for name in system_names:
        system = System(name=name, is_booked=False)
        db.session.add(system)

    db.session.commit()
