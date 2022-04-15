from flask import Flask, request, send_from_directory, render_template, redirect, url_for
from flask_dance.contrib.github import make_github_blueprint, github
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from time import time
import finnhub
finnhub_client = finnhub.Client(api_key="c9cdsciad3i8nttpf2pg")

# app = Flask(__name__)
app = Flask(__name__,
            static_url_path='', 
            static_folder='assets',
            template_folder='views')
CORS(app)
app.secret_key = "please_define_a_secret_key_here"
app.config["GITHUB_OAUTH_CLIENT_ID"] = 'eac3bb989c74957c1c7a'
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = 'b41d1c91bc657ab3db0dc5d65d089be102a73d46'
blueprint = make_github_blueprint()
app.register_blueprint(make_github_blueprint(), url_prefix="/login")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./test.db'
db = SQLAlchemy(app)

class UserStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=False, nullable=False)
    symbol = db.Column(db.String(50), unique=False, nullable=False)

    def __repr__(self):
        return '<UserStock %r>' % self.username + ' ' + self.symbol  

db.drop_all()
db.create_all()
# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"

@app.route("/")
def index():
    general_news = finnhub_client.general_news('general', min_id=0)
    if github.authorized:
        github_user = github.get("/user").json()
        return render_template( 'index.html', title = ' - Index', login = github_user['login'], general_news = general_news)
    else:
        return render_template('index.html', title = ' - Index', general_news = general_news)

@app.route("/login")
def login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    return redirect('/')

@app.route("/portfolio", methods = ['GET', 'POST'])
def portfolio():
    if not github.authorized:
        return redirect('/login')
    github_user = github.get("/user").json()
    if request.method == 'POST':
        symbol = request.form['symbol']
        db.session.add(UserStock(username=github_user['login'], symbol=symbol))
        db.session.commit()
    stocks = UserStock.query.filter_by(username=github_user['login'])
    return render_template('portfolio.html', login = github_user['login'], title = ' - Portfolio', stocks = stocks)

@app.route("/portfolio/<symbol>", methods=['DELETE'])
def deletePortfolio(symbol):
    if not github.authorized:
        return redirect('/login')

    github_user = github.get("/user").json()
    stocks = UserStock.query.filter_by(username=github_user['login'], symbol=symbol)
    for s in stocks:
        db.session.delete(s)
    db.session.commit()
    return 'ok'

