import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_apscheduler import APScheduler
from sqlalchemy_utils import database_exists


import csv


app = Flask(__name__)

""" APP CONFIGURATIONS """
basedir = os.path.abspath(os.path.dirname(__file__))
PATH_SQLITE_DB = 'sqlite:///' + os.path.join(basedir, 'opennews.db')

app.config['SECRET_KEY'] = 'fbfc2fec59bde3d8040e5e57dcb5c5e7'
app.config['SQLALCHEMY_DATABASE_URI'] = PATH_SQLITE_DB

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


""" CREATE DB IF IT DOES NOT ALREADY EXIST """

# https://stackoverflow.com/questions/44941757/sqlalchemy-exc-operationalerror-sqlite3-operationalerror-no-such-table
if not database_exists(PATH_SQLITE_DB): 
    
    # 1) Create Schema from models
    from .models import User, Article, Event, Publisher
    with app.app_context():
        db.create_all()

        # 2) Import publishers data
        with open("publishers.csv") as file:
            reader = csv.DictReader(file)

            for publisher_attr in reader:
                db.session.add(Publisher(**publisher_attr))

            db.session.commit()






scheduler = APScheduler()

from opennews import jobs

scheduler.init_app(app)
scheduler.start()

from opennews import routes