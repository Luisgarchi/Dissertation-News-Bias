from datetime import datetime
from opennews import db, login_manager
from flask_login import UserMixin



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

""" USER model """

class User(db.Model, UserMixin):
    id       = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email    = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(50), nullable = False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"



""" ARTICLE to TAG table, (many-to-many relationship) """

article_tag = db.Table('article_tag',
                    db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True),
                    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True))



"""ARTICLE model"""

class Article(db.Model):
    id             = db.Column(db.Integer, primary_key = True)
    url            = db.Column(db.Text, nullable = False)
    publisher_id   = db.Column(db.Integer, db.ForeignKey('publisher.id'), nullable = True)
    title          = db.Column(db.Text, nullable = False)
    maintext       = db.Column(db.Text, nullable = False)
    published_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    event_id       = db.Column(db.Integer, db.ForeignKey('event.id'), nullable = True)
    tags           = db.relationship('Tag', secondary = article_tag, lazy='subquery', backref=db.backref('articles', lazy=True))

    #lead           = db.Column(db.Text, nullable = False)
    
    def __repr__(self):
        return f"Article('{self.publisher}', '{self.date}', '{self.title}')"


""" TAG model """

class Tag(db.Model):
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable = False)



""" EVENT model"""

class Event(db.Model):
    id       = db.Column(db.Integer, primary_key = True)
    date     = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    about    = db.Column(db.Text, nullable = False)
    articles = db.relationship('Article', backref = 'event', lazy = True)

    def __repr__(self):
        return f"Event('{self.date}', '{self.about}')"


""" PUBLISHER model """

class Publisher(db.Model):
    id          = db.Column(db.Integer, primary_key = True)
    name        = db.Column(db.String(50), nullable = False)
    orientation = db.Column(db.String(2), nullable = False)
    route_url   = db.Column(db.Text, nullable = False)
    country     = db.Column(db.String(30), nullable = False)
    articles    = db.relationship('Article', backref = 'publisher', lazy = True)

    def __repr__(self):
        return f"Publisher('{self.name}', '{self.about}')"