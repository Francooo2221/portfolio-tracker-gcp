from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    holdings = db.relationship('Holding', backref='owner', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # ilość sztuk
    price_at_buy = db.Column(db.Float, nullable=False) # cena zakupu
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), unique=True, nullable=False) # np. 'BTC-USD', 'ALE.WA', 'AAPL'
    asset_type = db.Column(db.String(20)) # 'crypto', 'gpw', 'usa', 'metal'
    amount = db.Column(db.Float, default=0.0)
    current_price = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    # Relacja do cen historycznych
    prices = db.relationship('DailyPrice', backref='asset', lazy=True)

class DailyPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False) # Przechowujemy tylko datę (bez godziny)