from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Asset, Transaction, DailyPrice
from tasks import update_prices

app = Flask(__name__)
app.config['SECRET_KEY'] = 'giga-tajne-haslo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def dashboard():
    # Pobieramy aktywa użytkownika
    user_assets = Asset.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', assets=user_assets)

@app.route('/add', methods=['POST'])
@login_required
def add_transaction():
    ticker = request.form.get('ticker').upper()
    amount = float(request.form.get('amount'))
    price = float(request.form.get('buy_price'))
    
    # 1. Sprawdź czy użytkownik ma już to aktywo
    asset = Asset.query.filter_by(ticker=ticker, user_id=current_user.id).first()
    if not asset:
        asset = Asset(ticker=ticker, user_id=current_user.id, asset_type='stock')
        db.session.add(asset)
        db.session.commit() # Commit, żeby dostać ID dla transakcji
    
    # 2. Dodaj transakcję
    new_trans = Transaction(asset_id=asset.id, amount=amount, price_at_buy=price)
    db.session.add(new_trans)
    db.session.commit()
    
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/update-manual')
def manual_update():
    update_prices(app)
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password=generate_password_hash('admin123')))
            db.session.commit()
    app.run(host='0.0.0.0', port=8501)