import os
from flask import Flask
from models import db, Product, Category
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

ar_cats = {
    'Fertilizers': 'الأسمدة',
    'Pesticides': 'المبيدات',
    'Seeds': 'البذور',
    'Farming Tools': 'الأدوات الزراعية',
    'Safety Wearables': 'معدات السلامة',
    'Electronic Devices': 'الأجهزة الإلكترونية'
}

ar_prods = {
    'NPK Compound Fertilizer 20-20-20': 'سماد مركب NPK 20-20-20',
    'Organic Compost Fertilizer (5 KG)': 'سماد عضوي كومبوست (5 كجم)',
    'Urea Fertilizer 46% Nitrogen': 'سماد يوريا 46% نيتروجين',
    'BioShield Organic Pesticide Spray': 'رذاذ مبيد حشري عضوي بيوشيلد',
    'FungoClear Fungicide Concentrate': 'مبيد فطري مركز فونجوكليير',
    'Hybrid Tomato Seeds (F1) - 500g': 'بذور طماطم هجينة (F1) - 500 جم',
    'Sunflower Seeds - 1 KG Pack': 'بذور دوار الشمس - عبوة 1 كجم',
    'Maize/Corn Hybrid Seeds - 2 KG': 'بذور ذرة هجينة - 2 كجم',
    'Heavy Duty Garden Shovel': 'مجرفة حديقة شديدة التحمل',
    'Irrigation Drip Kit (100m)': 'طقم ري بالتنقيط (100 متر)',
    'Hand Trowel & Transplanter Set': 'طقم أدوات زراعة يدوية',
    'Chemical-Resistant Farming Gloves': 'قفازات زراعية مقاومة للمواد الكيميائية',
    'Agricultural Safety Boot (Size 42)': 'حذاء أمان زراعي (مقاس 42)',
    'Respirator Mask for Pesticide Spraying': 'قناع تنفس لرش المبيدات',
    'Soil pH & Moisture Sensor': 'مستشعر رطوبة وحموضة التربة',
    'Smart Weather Station for Farm': 'محطة طقس ذكية للمزرعة',
    'Automatic Plant Watering Timer': 'مؤقت ري تلقائي للنباتات'
}

with app.app_context():
    for c in Category.query.all():
        if c.name in ar_cats:
            c.name_ar = ar_cats[c.name]
            
    for p in Product.query.all():
        if p.name in ar_prods:
            p.name_ar = ar_prods[p.name]
            p.description_ar = "وصف باللغة العربية لهذا المنتج."
            
    db.session.commit()
    print("Arabic data seeded.")
