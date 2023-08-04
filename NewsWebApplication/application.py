from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from apptools import globalNews
import os

app = Flask(__name__)


""" APP CONFIGURATIONS """

app.config['SECRET_KEY'] = 'fbfc2fec59bde3d8040e5e57dcb5c5e7'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'opennews.db')


db = SQLAlchemy(app)

class User(db.Model):
    id       = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email    = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(50), nullable = False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    

# Many-to-Many relationship helper table
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
article_event = db.Table('article_events',
    db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
)

class Article(db.Model):
    id        = db.Column(db.Integer, primary_key = True)
    url       = db.Column(db.Text, nullable = False)
    publisher = db.Column(db.String(50), nullable = False)
    title     = db.Column(db.Text, nullable = False)
    lead      = db.Column(db.Text, nullable = False)
    maintext  = db.Column(db.Text, nullable = False)
    date      = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    # event     = db.Column(db.Integer, db.ForeignKey('event.id'), nullable = True)
    
    def __repr__(self):
        return f"User('{self.publisher}', '{self.date}', '{self.title}')"


class Event(db.Model):
    id       = db.Column(db.Integer, primary = True)
    date     = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    about    = db.Column(db.Text, nullable = False)
    articles = db.relationship('Article', secondary = article_event, backref = 'event', lazy = True)
    # article = db.Column(db.Integer, db.ForeignKey('article.id'), nullable = False)



""" CREATE DB FROM COMMAND LINE """
def create_db():
    with app.app_context():
        db.create_all()



""" HOME """

@app.route("/")
@app.route("/home")
def home():
    articles = globalNews()
    return render_template("home.html", articles = articles, title = "Top Stories")



""" REGISTER """

@app.route("/register", methods = ["GET", "POST"])
def register():

    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account create for {form.username.data}', 'success')
        return redirect(url_for('home'))
    

    return render_template('register.html', title = 'Register', form = form)





""" LOG IN """

@app.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        flash(f'Account create for {form.username.data}', 'success')
        return redirect(url_for('home'))
    elif form.is_submitted():
        flash('Login Unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html', title = 'Login', form = form)






if __name__ == '__main__':
    app.run(debug = True)