import yfinance as yf
from datetime import datetime
from models import db, Asset, DailyPrice


def update_all_prices(app):
    with app.app_context():
        assets = Asset.query.all()
        for asset in assets:
            try:
                ticker_data = yf.Ticker(asset.ticker)
                current_price = ticker_data.fast_info['last_price']
                
                new_price = DailyPrice(asset_id=asset.id, price=current_price)
                db.session.add(new_price)
                print(f"Zaktualizowano: {asset.ticker} - {current_price}")
            except Exception as e:
                print(f"Błąd przy {asset.ticker}: {e}")
        
        db.session.commit()