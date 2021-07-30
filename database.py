import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))
# pilnas kelias iki šio failo.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'autoplius_data.sqlite')
# nustatėme, kad mūsų duomenų bazė bus šalia šio failo esants data.sqlite failas
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# neseksime kiekvienos modifikacijos
db = SQLAlchemy(app)
# sukuriame duomenų bazės objektą


# sukurkime modelį užklausos formai, kuris sukurs duomenų bazėje lentelę
class Autoplius(db.Model):
    __tablename__ = 'scraped_data_final'
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String)
    model = db.Column(db.String)
    type = db.Column(db.String)
    year = db.Column(db.Integer)
    mileage = db.Column(db.Integer)
    tran = db.Column(db.String)
    engine = db.Column(db.Float)
    fuel = db.Column(db.String)
    price = db.Column(db.Integer)

    def __init__(self, make, model, type, year, mileage, tran, engine, fuel, price):
        self.make = make
        self.model = model
        self.type = type
        self.year = year
        self.mileage = mileage
        self.tran = tran
        self.engine = engine
        self.fuel = fuel
        self.price = price


class ModelByMake(db.Model):
    __tablename__ = 'scores_by_make'
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String)
    score = db.Column(db.Float)

    def __init__(self, make, score):
        self.make = make
        self.score = score
