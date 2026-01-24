import yfinance as yf
from datetime import date
from models import db, Holding, DailyPrice

def update_prices(app):
    with app.app_context():
        # Pobierz unikalne tickery wszystkich użytkowników
        unique_tickers = db.session.query(Holding.ticker).distinct().all()
        
        for (t_symbol,) in unique_tickers:
            ticker = yf.Ticker(t_symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                # Zapisz cenę do historii
                new_price_entry = DailyPrice(ticker=t_symbol, price=current_price, date=date.today())
                db.session.add(new_price_entry)
        
        db.session.commit()
        print("Ceny historyczne zaktualizowane.")