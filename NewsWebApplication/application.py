from flask import Flask, render_template
from apptools import globalNews

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    articles = globalNews()
    return render_template("home.html", articles = articles, title = "Top Stories")

@app.route("/")
def geohome():
    return None



if __name__ == '__main__':
    app.run(debug = True)
    