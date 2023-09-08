from flask import render_template, url_for, flash, redirect, request
from opennews import app, db, bcrypt
from opennews.forms import RegistrationForm, LoginForm
from opennews.models import User, Article, Event
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import func
import datetime

""" HOME """


@app.route("/")
@app.route("/home")
def home():

    utc_dt_aware = datetime.datetime.now(datetime.timezone.utc)
    date_last_day = utc_dt_aware - datetime.timedelta(days=1)
    
    #articles = Article.query.filter(Article.published_date >= date_last_day)

    event_ids =  [event_id[0] for event_id in db.session.query(Article.event_id, func.count(Article.event_id)).group_by(Article.event_id).having(func.count(Article.event_id) >= 2).all()]

    articles = []
    for id in event_ids:
        articles.append(Article.query.filter_by(event_id = id))
    
    print(articles)

    #db.session.query(Article).filter(Article.published_date >= date_last_day, Article.event_idin_() date_last_day).group_by(Article.event_id).having

    return render_template("home.html", articles = articles, title = "Top Stories")



""" REGISTER """


@app.route("/register", methods = ["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():

        # Hash password and save user in DB
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {form.username.data}', 'success')
        return redirect(url_for('login'))
    

    return render_template('register.html', title = 'Register', form = form)




""" LOG IN """


@app.route("/login", methods = ["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():

        # Check if user exists in DB
        user = User.query.filter_by(email = form.email.data).first()
        
        # Validate password and log user in
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            
            #Check for page redirect
            next_page = request.args.get('next')
            
            if next_page and next_page != '/':
                page = next_page[1:]                        # drops leading slash
                return redirect(url_for(page))         
            else:
                return redirect(url_for('home'))
        
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
        
    return render_template('login.html', title = 'Login', form = form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html', title = 'Profile')
