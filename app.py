from flask import Flask, request, send_from_directory, render_template, redirect, url_for
from flask_dance.contrib.github import make_github_blueprint, github
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from time import time
import finnhub
import time

finnhub_client = finnhub.Client(api_key="c9cdsciad3i8nttpf2pg")
# finnhub_client = finnhub.Client(api_key="c9ecaqiad3iff7bjnsgg")

# app = Flask(__name__)
app = Flask(__name__,
            static_url_path='',
            static_folder='assets',
            template_folder='views')
CORS(app)
app.secret_key = "please_define_a_secret_key_here"
# app.config["GITHUB_OAUTH_CLIENT_ID"] = 'eac3bb989c74957c1c7a'
# app.config["GITHUB_OAUTH_CLIENT_SECRET"] = 'b41d1c91bc657ab3db0dc5d65d089be102a73d46'
app.config["GITHUB_OAUTH_CLIENT_ID"] = 'fe75b86dc0f4e11eb2e0'
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = '849f52fb3dff1bf71ad1b7070e99544d6af16d7a'
blueprint = make_github_blueprint()
app.register_blueprint(make_github_blueprint(), url_prefix="/login")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./test.db'
db = SQLAlchemy(app)

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=False, nullable=False)
    number = db.Column(db.Integer, unique=False, nullable=False)
    time = db.Column(db.String(255), unique=False, nullable=False)

    def __repr__(self):
        return '<income %r>' % self.username + ' ' + self.number

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=False, nullable=False)
    number = db.Column(db.Integer, unique=False, nullable=True)
    stock = db.Column(db.String(255), unique=False, nullable=False)
    time = db.Column(db.String(255), unique=False, nullable=False)

    def __repr__(self):
        return '<payment %r>' % self.username + ' ' + self.symbol + ' ' + self.number

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=False, nullable=False)

    def __repr__(self):
        return '<Users %r>' % self.username + ' ' + self.username

# db.drop_all()
db.create_all()


@app.route("/")
def index():
    general_news = finnhub_client.general_news('general', min_id=0)
    if github.authorized:
        github_user = github.get("/user").json()
        return render_template('index.html', title=' - Index', login=github_user['login'], general_news=general_news)
    else:
        return render_template('index.html', title=' - Index', general_news=general_news)


@app.route("/login")
def login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    return redirect('/')

@app.route("/income", methods=['GET', 'POST'])
def income():
    # Get the total number of income
    if not github.authorized:
        return redirect('/login')
    github_user = github.get("/user").json()
    # print("????????? " + sum)
    if request.method == 'GET':
        incomeNum = Income.query.filter_by(username=github_user['login'])
        sum = db.session.query(func.sum(Income.number)).scalar()
        return render_template('income.html', login=github_user['login'], title=' - Income',incomeNum=incomeNum, sum=sum)
    if request.method == 'POST':
        incomeNum = request.form['incomeNum']
        currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if incomeNum != '':
            db.session.add(Income(username=github_user['login'], number=incomeNum, time=currentTime))
            db.session.commit()
    incomeNum = Income.query.filter_by(username=github_user['login'])
    sum = db.session.query(func.sum(Income.number)).scalar()
    return render_template('income.html', login=github_user['login'], title=' - Income', incomeNum=incomeNum, sum=sum)


@app.route("/payment", methods=['GET', 'POST'])
def payment():
    if not github.authorized:
        return redirect('/login')
    github_user = github.get("/user").json()
    if request.method == 'GET':
        paymentNum = Payment.query.filter_by(username=github_user['login'])
        sum = db.session.query(func.sum(Payment.number)).scalar()
        return render_template('payment.html', login=github_user['login'], title=' - Income', paymentNum=paymentNum, sum=sum)
    if request.method == 'POST':
        paymentNum = request.form['paymentNum']
        paymentType = request.form['paymentType']
        stockName = request.form['stockName']
        stockName = stockName.upper()
        currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if paymentType == "0":
            db.session.add(Payment(username=github_user['login'], number=paymentNum, stock="Normal", time=currentTime))
        else:
            db.session.add(Payment(username=github_user['login'], number=paymentNum, stock=stockName, time=currentTime))
        db.session.commit()
    paymentNum = Payment.query.filter_by(username=github_user['login'])
    sum = db.session.query(func.sum(Payment.number)).scalar()
    return render_template('payment.html', login=github_user['login'], title=' - Income', paymentNum=paymentNum, sum=sum)

@app.route("/income/<id>", methods=['DELETE'])
def deleteIncome(id):
    if not github.authorized:
        return redirect('/login')

    incomeNum = Income.query.filter_by(id=id)
    for s in incomeNum:
        db.session.delete(s)
    db.session.commit()
    return 'ok'

@app.route("/payment/<id>", methods=['DELETE'])
def deletePayment(id):
    if not github.authorized:
        return redirect('/login')

    paymentNum = Payment.query.filter_by(id=id)
    for s in paymentNum:
        db.session.delete(s)
    db.session.commit()
    return 'ok'


# @app.route("/addIncome", methods=['GET', 'POST'])
# def payment():
#
#     return 0


# @app.route("/portfolio/<symbol>", methods=['DELETE'])
# def deletePortfolio(symbol):
#     if not github.authorized:
#         return redirect('/login')
#
#     github_user = github.get("/user").json()
#     stocks = UserStock.query.filter_by(
#         username=github_user['login'], symbol=symbol)
#     for s in stocks:
#         db.session.delete(s)
#     db.session.commit()
#     return 'ok'
