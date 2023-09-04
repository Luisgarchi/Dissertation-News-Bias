from datetime import datetime
from opennews import db, login_manager
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method



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



""" ARTICLE to ENNTITY table, (many-to-many relationship) """

article_entity = db.Table('article_entity',
                    db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True),
                    db.Column('entity_id', db.Integer, db.ForeignKey('entity.id'), primary_key=True),
                    db.Column('polarity', db.Numeric(precision=3, scale=2), nullable = False),
                    db.Column('count', db.Integer, nullable = False),
                    db.Column('top', db.Boolean, default=False, nullable=False))



"""ARTICLE model"""

class Article(db.Model):
    id             = db.Column(db.Integer, primary_key = True)
    url            = db.Column(db.Text, nullable = False, unique = True)
    publisher_id   = db.Column(db.Integer, db.ForeignKey('publisher.id'), nullable = True)
    title          = db.Column(db.Text, nullable = False)
    maintext       = db.Column(db.Text, nullable = False)
    published_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    event_id       = db.Column(db.Integer, db.ForeignKey('event.id'), nullable = True)
    polarity       = db.Column(db.Numeric(precision=3, scale=2), default = 0, nullable = False)
    subjectivity   = db.Column(db.Numeric(precision=3, scale=2), default = 0, nullable = False)
    entities       = db.relationship('Entity', secondary = article_entity, lazy='subquery', backref=db.backref('articles', lazy=True))
    lead           = db.Column(db.Text, nullable = False)
    


    """
    # https://docs.sqlalchemy.org/en/20/orm/extensions/hybrid.html
    @hybrid_method
    def cosine_similarity(self, other): 
        return compute_cosine_CV(other, split(self.lead), tokenized = False)
    
    @hybrid_property
    def split(self):

    @cosine_similarity.expression
    def cosine_similarity(cls, other):
        return compute_cosine_CV(other, cls.lead, tokenized = False)
    """

    
    def __repr__(self):
        return f"Article('{self.publisher}', '{self.date}', '{self.title}')"


""" ENTITY model """

class Entity(db.Model):
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable = False)
    kb_id = db.Column(db.String(50), nullable = False, unique = True)



""" EVENT model"""

class Event(db.Model):
    id       = db.Column(db.Integer, primary_key = True)
    date     = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    first_url= db.Column(db.Text, nullable = False)
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