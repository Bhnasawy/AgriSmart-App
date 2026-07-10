import os
from flask import Flask
from models import db, Product, Category
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

ar_prods = {
    'Cantaloupe seeds 8g': 'بذور كانتالوب 8 جم',
    'Lettuce seeds 15g': 'بذور خس 15 جم',
}

with app.app_context():
    for p in Product.query.all():
        if p.name in ar_prods:
            p.name_ar = ar_prods[p.name]
            p.description_ar = "وصف باللغة العربية لهذا المنتج."
            
    db.session.commit()
    print("New products translated.")
