from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'giga-tajne-haslo-zmien-mnie'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    holdings = db.relationship('Holding', backref='owner', lazy=True)

class Holding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    date_bought = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def dashboard():
    user_holdings = Holding.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', holdings=user_holdings)

@app.route('/add', methods=['POST'])
@login_required
def add_holding():
    ticker = request.form.get('ticker').upper()
    amount = float(request.form.get('amount'))
    buy_price = float(request.form.get('buy_price'))
    
    new_holding = Holding(ticker=ticker, amount=amount, buy_price=buy_price, owner=current_user)
    db.session.add(new_holding)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Błędny login lub hasło')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- INICJALIZACJA (Tylko dla Ciebie, żeby stworzyć admina) ---
def create_admin():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            hashed_pw = generate_password_hash('HASLO_Z_ANSIBLE', method='pbkdf2:sha256')
            admin = User(username='admin', password=hashed_pw)
            db.session.add(admin)
            db.session.commit()
            print("Konto admina stworzone: admin / TwojeHaslo123")

if __name__ == '__main__':
    create_admin()
    app.run(host='0.0.0.0', port=8501)