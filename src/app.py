from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Asset, Transaction, DailyPrice
from tasks import update_all_prices
from apscheduler.schedulers.background import BackgroundScheduler
import yfinance as yf
from flask import jsonify
from datetime import datetime



app = Flask(__name__)
app.config['SECRET_KEY'] = 'giga-tajne-haslo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/get_live_price/<ticker>')
@login_required
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker)
        # Pobieramy ostatnią cenę
        price = data.fast_info['last_price']
        return jsonify({'price': round(price, 2)})
    except Exception as e:
        return jsonify({'error': 'Nie znaleziono tickera'}), 404
    
@app.route('/analytics')
@login_required
def analytics():
    user_assets = Asset.query.filter_by(user_id=current_user.id).all()
    
    asset_labels, asset_values = [], []
    type_data = {}
    all_tickers_data = {}
    all_dates = set()

    # 1. Pobieramy dane dla każdego tickera
    for asset in user_assets:
        try:
            ticker = yf.Ticker(asset.ticker)
            hist = ticker.history(period="max")
        except:
            hist = None

        if hist is not None and not hist.empty:
            # Dane do "tortu" (aktualne)
            last_price = hist['Close'].iloc[-1]
            current_val = round(asset.total_amount * last_price, 2)

            if asset.total_amount > 0:
                asset_labels.append(asset.ticker)
                asset_values.append(current_val)
                t_name = (asset.asset_type or "Inne").upper()
                type_data[t_name] = type_data.get(t_name, 0) + current_val

            # Dane do osi czasu
            hist.index = hist.index.strftime('%Y-%m-%d')
            all_tickers_data[asset.ticker] = {
                'prices': hist['Close'].to_dict(),
                'amount': asset.total_amount,
                'first_price': hist['Close'].iloc[0]
            }
            all_dates.update(hist.index.tolist())
        
        elif asset.total_amount > 0:
            # Aktywa 'Inne' (nieruchomości)
            last_p = asset.transactions[-1].price_at_buy if asset.transactions else 0
            val = round(asset.total_amount * last_p, 2)
            asset_labels.append(asset.ticker)
            asset_values.append(val)
            t_name = (asset.asset_type or "Inne").upper()
            type_data[t_name] = type_data.get(t_name, 0) + val

    # 2. Budujemy historię
    sorted_dates = sorted(list(all_dates))
    temp_labels, temp_values, temp_profit = [], [], []
    
    last_known_prices = {t: 0 for t in all_tickers_data}
    first_prices = {t: data['first_price'] for t, data in all_tickers_data.items()}

    for d_str in sorted_dates:
        day_val = 0
        day_cost = 0
        for ticker, data in all_tickers_data.items():
            if d_str in data['prices']:
                last_known_prices[ticker] = data['prices'][d_str]
            day_val += last_known_prices[ticker] * data['amount']
            day_cost += first_prices[ticker] * data['amount']

        # Dodajemy do tymczasowych list tylko jeśli wartość portfela > 0
        # To automatycznie usunie "puste lata" (np. od 1990 do 2020)
        if day_val > 0.1:
            temp_labels.append(d_str)
            temp_values.append(round(day_val, 2))
            temp_profit.append(round(day_val - day_cost, 2))

    # 3. Finalna agregacja (żeby wykres był chudy i smukły)
    line_labels = []
    value_history = []
    profit_history = []
    
    # Wybieramy co 5. punkt z przefiltrowanej już listy (tylko tam gdzie masz kasę)
    for i in range(len(temp_labels)):
        if i % 5 == 0 or i == len(temp_labels) - 1:
            line_labels.append(temp_labels[i])
            value_history.append(temp_values[i])
            profit_history.append(temp_profit[i])

    return render_template('analytics.html', 
                           asset_labels=asset_labels, 
                           asset_values=asset_values,
                           type_labels=list(type_data.keys()), 
                           type_values=list(type_data.values()),
                           line_labels=line_labels, 
                           value_history=value_history,    
                           profit_history=profit_history)

@app.route('/')
@login_required
def dashboard():
    user_assets = Asset.query.filter_by(user_id=current_user.id).all()
    holdings = []
    
    for asset in user_assets:
        # 1. Pobieramy transakcje posortowane chronologicznie
        transactions = sorted(asset.transactions, key=lambda x: x.id)
        
        current_qty = 0
        total_cost_basis = 0
        
        # 2. Obliczamy koszt bazowy metodą średniej ważonej
        for t in transactions:
            if t.amount > 0:  # KUPNO
                current_qty += t.amount
                total_cost_basis += t.amount * t.price_at_buy
            else:  # SPRZEDAŻ (t.amount jest ujemne)
                if current_qty > 0:
                    avg_buy_price = total_cost_basis / current_qty
                    current_qty += t.amount
                    # Zmniejszamy koszt proporcjonalnie do średniej ceny zakupu
                    total_cost_basis += t.amount * avg_buy_price
                else:
                    current_qty += t.amount

        # 3. Jeśli faktycznie coś jeszcze posiadamy
        if current_qty > 0:
            # Pobieramy ostatnią cenę z bazy daily_prices
            last_price_record = DailyPrice.query.filter_by(asset_id=asset.id)\
                                .order_by(DailyPrice.date.desc()).first()
            current_price = last_price_record.price if last_price_record else 0
            
            # Obliczenia końcowe
            current_value = current_qty * current_price
            # Zysk tylko dla aktywów, które wciąż mamy w portfelu
            profit_val = current_value - total_cost_basis
            profit_pct = (profit_val / total_cost_basis * 100) if total_cost_basis > 0 else 0

            holdings.append({
                'ticker': asset.ticker,
                'asset_type': asset.asset_type,
                'amount': current_qty,
                'current_price': current_price,
                'value': current_value,
                'profit_val': profit_val, # Kwota zysku
                'profit': profit_pct      # Procent zysku
            })
    if holdings:
        total_portfolio_value = sum(h['value'] for h in holdings)
        total_portfolio_profit = sum(h['profit_val'] for h in holdings)
        total_cost = total_portfolio_value - total_portfolio_profit
        total_profit_pct = (total_portfolio_profit / total_cost * 100) if total_cost > 0 else 0
    else:
        total_portfolio_value = 0.0
        total_portfolio_profit = 0.0
        total_profit_pct = 0.0
        total_cost = 0.0

    return render_template('dashboard.html', 
                                holdings=holdings, 
                                total_val=total_portfolio_value, 
                                total_profit=total_portfolio_profit,
                                total_pct=total_profit_pct)
            


@app.route('/add', methods=['POST'])
@login_required
def add_transaction():
    ticker = request.form.get('ticker').upper()
    if request.form.get('transcation_type') == 'buy':
        amount = float(request.form.get('amount'))
    else:
        amount = -float(request.form.get('amount'))
    price = float(request.form.get('buy_price'))
    asset_type = request.form.get('asset_type').lower()

    # 1. Sprawdź czy użytkownik ma już to aktywo
    asset = Asset.query.filter_by(ticker=ticker, user_id=current_user.id).first()
    if not asset:
        if request.form.get('transcation_type') == 'sell':
            flash('Nie można sprzedać aktywa, którego nie posiadasz!')
            return redirect(url_for('dashboard'))
        asset = Asset(ticker=ticker, user_id=current_user.id, asset_type=asset_type)
        db.session.add(asset)
        db.session.commit() # Commit, żeby dostać ID dla transakcji
    
    # 2. Dodaj transakcję
    new_trans = Transaction(asset_id=asset.id, amount=amount, price_at_buy=price)
    if amount + asset.total_amount < 0:
        flash('Nie można sprzedać więcej niż posiadasz!')
        return redirect(url_for('dashboard'))
    db.session.add(new_trans)
    new_daily_price = DailyPrice(
        asset_id=asset.id,
        price=price, # Skoro właśnie to kupiłeś, to jest to nasza "aktualna" cena na start
        date=datetime.utcnow()
    )
    db.session.add(new_daily_price)
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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Zostałeś wylogowany.')
    return redirect(url_for('login'))

scheduler = BackgroundScheduler()
scheduler.add_job(func=update_all_prices, trigger="interval", minutes=5, args=[app])
scheduler.start()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password=generate_password_hash('admin123')))
            db.session.commit()
    app.run(host='0.0.0.0',debug=True, port=8501)