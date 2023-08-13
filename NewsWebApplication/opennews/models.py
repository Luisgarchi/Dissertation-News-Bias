from datetime import datetime
from opennews import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id       = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email    = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(50), nullable = False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Article(db.Model):
    id             = db.Column(db.Integer, primary_key = True)
    url            = db.Column(db.Text, nullable = False)
    publisher_id   = db.Column(db.Integer, db.ForeignKey('publisher.id'), nullable = True)
    title          = db.Column(db.Text, nullable = False)
    maintext       = db.Column(db.Text, nullable = False)
    published_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    event_id       = db.Column(db.Integer, db.ForeignKey('event.id'), nullable = True)
    
    #keys           = db.Column 

    #publisher      = db.Column(db.String(50), nullable = False)
    #lead           = db.Column(db.Text, nullable = False)
    
    def __repr__(self):
        return f"Article('{self.publisher}', '{self.date}', '{self.title}')"


class Event(db.Model):
    id       = db.Column(db.Integer, primary_key = True)
    date     = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    about    = db.Column(db.Text, nullable = False)
    articles = db.relationship('Article', backref = 'event', lazy = True)
    # article = db.Column(db.Integer, db.ForeignKey('article.id'), nullable = False)

    def __repr__(self):
        return f"Event('{self.date}', '{self.about}')"


class Publisher(db.Model):
    id          = db.Column(db.Integer, primary_key = True)
    name        = db.Column(db.String(50), nullable = False)
    orientation = db.Column(db.String(2), nullable = False)
    route_url   = db.Column(db.Text, nullable = False)
    country     = db.Column(db.String(30), nullable = False)
    articles    = db.relationship('Article', backref = 'publisher', lazy = True)

    def __repr__(self):
        return f"Publisher('{self.name}', '{self.about}')"