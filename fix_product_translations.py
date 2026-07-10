import os
from flask import Flask
from models import db, Product
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

ar_products = {
    'NPK Compound Fertilizer 20-20-20': 'سماد NPK مركب 20-20-20',
    'Organic Compost Fertilizer (5 KG)': 'سماد عضوي طبيعي (5 كجم)',
    'Urea Fertilizer 46% Nitrogen': 'سماد يوريا 46٪ نيتروجين',
    'BioShield Organic Pesticide Spray': 'بخاخ مبيد حشري عضوي بيوشيلد',
    'FungoClear Fungicide Concentrate': 'مبيد فطري مركز فونجوكلير',
    'Hybrid Tomato Seeds (F1) - 500g': 'بذور طماطم هجينة (F1) - 500 جرام',
    'Sunflower Seeds - 1 KG Pack': 'بذور عباد الشمس - عبوة 1 كجم',
    'Maize/Corn Hybrid Seeds - 2 KG': 'بذور ذرة هجينة - 2 كجم',
    'Heavy Duty Garden Shovel': 'مجرفة حديقة شديدة التحمل',
    'Irrigation Drip Kit (100m)': 'طقم ري بالتنقيط (100 متر)',
    'Hand Trowel & Transplanter Set': 'مجموعة أدوات يدوية للزراعة',
    'Chemical-Resistant Farming Gloves': 'قفازات زراعية مقاومة للمواد الكيميائية',
    'Agricultural Safety Boot (Size 42)': 'حذاء أمان زراعي (مقاس 42)',
    'Respirator Mask for Pesticide Spraying': 'قناع تنفس لرش المبيدات',
    'Soil pH & Moisture Sensor': 'مستشعر رطوبة وحموضة التربة',
    'Smart Weather Station for Farm': 'محطة طقس ذكية للمزرعة',
    'Automatic Plant Watering Timer': 'مؤقت آلي لري النباتات',
    
    # Custom products the user added
    'Cantaloupe seeds 8g': 'بذور كانتالوب 8 ج',
    'lettuce seeds': 'بذور الخس',
    'yellow carrots 5 grams': 'جزر أصفر 5 جرام',
}

ar_descriptions = {
    'NPK Compound Fertilizer 20-20-20': 'سماد محبب متوازن يوفر كميات متساوية من النيتروجين والفوسفور والبوتاسيوم لتنمية المحاصيل بشكل شامل. مثالي للخضروات والفواكه والحبوب.',
    'Organic Compost Fertilizer (5 KG)': 'سماد عضوي غني مصنوع من مواد طبيعية. يحسن بنية التربة واحتفاظها بالماء والنشاط الميكروبي. 100% خالي من المواد الكيميائية.',
    'Urea Fertilizer 46% Nitrogen': 'سماد يوريا عالي النيتروجين يعزز نمو الأوراق السريع. مناسب للحبوب وقصب السكر ومعظم المحاصيل الحقلية.',
    'BioShield Organic Pesticide Spray': 'بخاخ مبيد حشري نباتي صديق للبيئة فعال ضد المن والعث والذباب الأبيض. آمن للحشرات النافعة والبشر.',
    'FungoClear Fungicide Concentrate': 'مبيد فطري واسع الطيف لمكافحة البياض الدقيقي واللفحة وأمراض الصدأ. تأثير جهازي لحماية تدوم طويلاً.',
    'Hybrid Tomato Seeds (F1) - 500g': 'بذور طماطم هجينة F1 عالية الإنتاجية ومقاومة للأمراض. تنتج ثماراً حمراء كبيرة صلبة. مناسبة للزراعة في الدفيئات والحقول المفتوحة.',
    'Sunflower Seeds - 1 KG Pack': 'بذور عباد شمس ممتازة غير معدلة وراثياً مناسبة لإنتاج الزيت والوجبات الخفيفة. معدل إنبات سريع بنسبة 95%.',
    'Maize/Corn Hybrid Seeds - 2 KG': 'بذور ذرة هجينة تتحمل الجفاف وتحتوي على نسبة عالية من النشا. مثالية لتغذية الحيوانات والاستهلاك البشري. تنتج ما يصل إلى 8 أطنان/هكتار.',
    'Heavy Duty Garden Shovel': 'مجرفة ممتازة من الفولاذ المقاوم للصدأ مع مقبض مريح على شكل حرف D. تصميم يقلل من التعب. مناسبة للحفر والزراعة وتقليب التربة.',
    'Irrigation Drip Kit (100m)': 'مجموعة ري بالتنقيط كاملة لـ 100 متر من الصفوف. تشمل الأنبوب الرئيسي والمنقطات والوصلات والفلتر. يوفر ما يصل إلى 60% من المياه.',
    'Hand Trowel & Transplanter Set': 'مجموعة من 3 أدوات يدوية مريحة: مجرفة، أداة نقل، ومحراث. رؤوس من الفولاذ المقاوم للصدأ مع مقابض مطاطية مضادة للانزلاق.',
    'Chemical-Resistant Farming Gloves': 'قفازات نتريل شديدة التحمل مع سوار ممتد لحماية المعصم. مقاومة للأسمدة والمبيدات والمذيبات. مقاس واحد يناسب الجميع.',
    'Agricultural Safety Boot (Size 42)': 'أحذية مطاطية مقاومة للماء مع غطاء إصبع القدم الفولاذي ونعل مضاد للانزلاق. مثالية لظروف الحقل الرطبة. متوفرة بأحجام متعددة.',
    'Respirator Mask for Pesticide Spraying': 'قناع تنفس نصف وجه مزود بمرشحات P100 مزدوجة. يحمي من الأبخرة الكيميائية ورذاذ المبيدات وجزيئات الغبار.',
    'Soil pH & Moisture Sensor': 'جهاز اختبار التربة الرقمي 3 في 1 يقيس درجة الحموضة والرطوبة وكثافة الضوء. لا حاجة للبطاريات. قراءات فورية لإدارة مثالية للمحاصيل.',
    'Smart Weather Station for Farm': 'محطة طقس لاسلكية بشاشة LCD. تراقب درجة الحرارة والرطوبة وهطول الأمطار وسرعة الرياح ومؤشر الأشعة فوق البنفسجية. تتضمن الاتصال بتطبيق الهاتف المحمول.',
    'Automatic Plant Watering Timer': 'مؤقت ري رقمي قابل للبرمجة لخراطيم الحديقة. اضبط ما يصل إلى 16 دورة ري في اليوم. غلاف متين ومقاوم للعوامل الجوية.',
    
    # Custom products
    'Cantaloupe seeds 8g': 'بذور كانتالوب نقية، 8 جرام',
    'lettuce seeds': 'بذور خس جيدة للزراعة',
    'yellow carrots 5 grams': 'جزر أصفر، وزن 5 جرام'
}

with app.app_context():
    count = 0
    for p in Product.query.all():
        if p.name in ar_products:
            p.name_ar = ar_products[p.name]
            p.description_ar = ar_descriptions.get(p.name, p.description)
            count += 1
    db.session.commit()
    print(f"Successfully translated {count} products to proper Arabic.")
