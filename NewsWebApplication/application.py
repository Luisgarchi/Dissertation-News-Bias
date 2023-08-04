from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from apptools import globalNews

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fbfc2fec59bde3d8040e5e57dcb5c5e7'

@app.route("/")
@app.route("/home")
def home():
    articles = globalNews()
    return render_template("home.html", articles = articles, title = "Top Stories")



"""
@app.route("/")
def geohome():
    return None
"""


@app.route("/register", methods = ["GET", "POST"])
def register():

    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account create for {form.username.data}', 'success')
        return redirect(url_for('home'))
    

    return render_template('register.html', title = 'Register', form = form)

@app.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit(): # CHANGEEEEEE
        flash(f'Account create for {form.username.data}', 'success')
        return redirect(url_for('home'))
    else:
        flash('Login Unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html', title = 'Login', form = form)

if __name__ == '__main__':
    app.run(debug = True)