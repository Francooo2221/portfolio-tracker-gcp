from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Holding, DailyPrice
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'giga-tajne-haslo-zmien-mnie'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- TRASY ---

@app.route('/')
@login_required
def dashboard():
    user_holdings = Holding.query.filter_by(user_id=current_user.id).all()
    # Tutaj w przyszłości dodamy pobieranie cen z DailyPrice, żeby liczyć zysk
    return render_template('dashboard.html', holdings=user_holdings)

@app.route('/add', methods=['POST'])
@login_required
def add_holding():
    ticker = request.form.get('ticker').upper()
    amount = float(request.form.get('amount'))
    buy_price = float(request.form.get('buy_price'))
    asset_type = request.form.get('asset_type', 'usa')
    
    new_holding = Holding(
        ticker=ticker, 
        amount=amount, 
        buy_price=buy_price, 
        asset_type=asset_type,
        owner=current_user
    )
    db.session.add(new_holding)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Błędny login lub hasło')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

def init_system():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            hashed_pw = generate_password_hash('TwojeHaslo123', method='pbkdf2:sha256')
            admin = User(username='admin', password=hashed_pw)
            db.session.add(admin)
            db.session.commit()
            print("System zainicjalizowany: Konto admin stworzone.")

if __name__ == '__main__':
    init_system()
    app.run(host='0.0.0.0', port=8501) # Zmieniłem na 5000, bo to standard Clouda