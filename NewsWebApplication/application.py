from flask import Flask, render_template
from apptools import globalNews

app = Flask(__name__)


posts = [
    {
        'publisher': 'BBC',
        'title': 'Zelensky after Moscow drone attack: War coming back to Russia',
        'maintext': """Ukraine's President Volodymyr Zelensky has warned war is coming back to Russia after a drone attack on the capital Moscow. Mr Zelensky said attacks on Russian territory were an "inevitable, natural and absolutely fair process" of the war between the two countries. Russia's defence ministry said three Ukrainian drones were downed on Sunday, with two crashing into offices.""",
        'date_posted': 'April 20, 2018',
        'url' : 'https://www.bbc.com/news/world-europe-66352765'
    },

    {
        'publisher': 'Independent',
        'title': 'War is returning to Russia, Zelensky warns, as Moscow rocked by drone attacks',
        'maintext': """War is returning to Russia, Ukraine's president Volodymyr Zelensky has warned, after early-morning drone attacks rocked Moscow. Although Ukraine has not claimed responsibility for Sunday’s attempted strikes, Mr Zelensky said such attacks were an "inevitable, natural, and absolutely fair process" of the war between the nations.""",
        'date_posted': 'April 21, 2018',
        'url' :  'https://www.independent.co.uk/news/world/europe/moscow-drone-attacks-zelensky-russia-ukraine-b2384581.html'
    }
]


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
    