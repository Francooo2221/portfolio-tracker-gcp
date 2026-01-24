import yfinance as yf
from datetime import date
from models import db, Asset, DailyPrice

def update_prices(app):
    with app.app_context():
        # Pobieramy unikalne aktywa
        all_assets = Asset.query.all()
        
        for asset in all_assets:
            try:
                ticker_data = yf.Ticker(asset.ticker)
                hist = ticker_data.history(period="1d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    new_price = DailyPrice(
                        asset_id=asset.id,
                        price=current_price,
                        date=date.today()
                    )
                    db.session.add(new_price)
            except Exception as e:
                print(f"Błąd dla {asset.ticker}: {e}")
        
        db.session.commit()