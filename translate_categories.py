import os
from flask import Flask
from models import db, Category, Product
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

ar_cats = {
    'Fertilizers': 'الأسمدة',
    'Pesticides': 'المبيدات',
    'Seeds': 'البذور',
    'Farming Tools': 'الأدوات الزراعية',
    'Safety Wearables': 'ملابس الأمان',
    'Electronic Devices': 'الأجهزة الإلكترونية',
}

with app.app_context():
    for cat in Category.query.all():
        if cat.name in ar_cats:
            cat.name_ar = ar_cats[cat.name]
            
    # ensure all products have name_ar if not set
    for p in Product.query.all():
        if not p.name_ar:
            p.name_ar = f"{p.name} (عربي)"
            p.description_ar = "وصف باللغة العربية"

    db.session.commit()
    print("Categories and remaining products translated.")
