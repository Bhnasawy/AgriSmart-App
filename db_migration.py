from models import db, Category, Product

ar_cats = {
    'Fertilizers': 'الأسمدة',
    'Pesticides': 'المبيدات',
    'Seeds': 'البذور',
    'Farming Tools': 'الأدوات الزراعية',
    'Safety Wearables': 'ملابس الأمان',
    'Electronic Devices': 'الأجهزة الإلكترونية',
}

ar_products = {
    'Heavy Duty Garden Shovel': 'مجرفة حديقة شديدة التحمل',
    'Irrigation Drip Kit (100m)': 'طقم ري بالتنقيط (100 متر)',
    'Automatic Plant Watering Timer': 'مؤقت آلي لري النباتات',
    'سماد هيومك اسيد 50 جم': 'سماد هيوميك أسيد 50 جم',
    'NPK 19-19-19 TE': 'سماد NPK 19-19-19 TE',
    'Fence shears': 'مقص سياج',
    'farming gloves': 'قفازات زراعية',
    'German pot 30 cm': 'إصيص ألماني 30 سم',
    'Digging Shovel': 'مجرفة حفر',
    '2 liter air pressure sprayer': 'بخاخ ضغط هواء 2 لتر',
    'Backpack Sprayer': 'بخاخ ظهر',
    'drip irrigation tubing': 'أنابيب ري بالتنقيط',
    'salinity meter': 'مقياس ملوحة',
    'Measures Moisture, pH,': 'مقياس رطوبة وحموضة',
    'Organic sulfur 50g': 'كبريت عضوي 50 جم',
    'Zucchini with 15 seeds': 'بذور كوسة 15 بذرة',
    'yellow carrots 5 grams': 'جزر أصفر 5 جرام',
    'Cantaloupe seeds 8g': 'بذور كانتالوب 8 جرام',
    'Watermelon seeds 7g': 'بذور بطيخ 7 جرام',
    '8 grams of cucumber seeds': 'بذور خيار 8 جرام',
    'Lettuce seeds 15g': 'بذور خس 15 جرام',
    'Rooting hormone': 'هرمون تجذير',
    'Humic + Algae, 1 kg': 'هيوميك وطحالب 1 كجم',
    'Volvic 1 kg': 'فولفيك 1 كجم',
    '5-liter salinity treatment': 'معالج ملوحة 5 لتر',
    'Picol 25% EC - Weight 250 cm': 'بيكول 25% EC - 250 سم',
    'Rizlux-T 50% pesticide, 100 grams': 'مبيد ريزلوكس-تي 50%، 100 جرام',
    'Copper sulfate, 100 grams': 'كبريتات نحاس، 100 جرام',
    'brown agricultural shovel': 'مجرفة زراعية بنية',
    'Essential Gardening Hand Tools': 'أدوات حدائق يدوية أساسية',
    '5g tomato seeds': 'بذور طماطم 5 جرام',
    'Watercress seeds 20g': 'بذور جرجير 20 جرام',
    'Carnation flower seeds': 'بذور زهرة القرنفل',
    'Basil seeds 25g': 'بذور ريحان 25 جرام',
    'sweet corn, 15 seeds': 'بذور ذرة حلوة، 15 بذرة',
    'Strawberry seeds': 'بذور فراولة',
    'Wade Killer 74.7%': 'مبيد حشائش ويد كيلر 74.7%',
    'Zinc 13% - 1 kg': 'زنك 13% - 1 كجم',
    'Full Body Chemical Protection Hazmat Suit': 'بدلة حماية كيميائية كاملة',
    'Waterproof Rubber Gardening Boots': 'أحذية مطاطية مقاومة للماء للزراعة',
    'Chemical Splashing Protection Kit': 'طقم حماية من الرذاذ الكيميائي',
    'Leather Gardening & Work Gloves': 'قفازات عمل وحدائق جلدية',
    'thiamethoxam | Chemical Insecticide': 'مبيد حشري كيميائي ثياميثوكسام',
    'Neem Oil, 1(30 ml)': 'زيت النيم، 30 مل',
    'Abamectin 1.8%': 'أبامكتين 1.8%',
    'Copper Fungicide': 'مبيد فطري نحاسي',
    'Azoxystrobin 25%': 'أزوكسيستروبين 25%',
    'Chlorothalonil  Fungicide': 'مبيد فطري كلوروثالونيل',
    'MANZEB 75% WP': 'مانزيب 75% WP',
    'Copper oxychloride': 'أوكسي كلوريد النحاس',
    'Copper Hydroxide': 'هيدروكسيد النحاس',
    'Copper Oxychloride 50 WP': 'أوكسي كلوريد النحاس 50 WP',
    'Retractable water hose with reel – 20 meters': 'خرطوم مياه قابل للسحب مع بكرة - 20 متر',
    'Micronized sulfur 30g': 'كبريت ميكروني 30 جرام',
    'Pure 2L Sprayer with Spray Attachment': 'بخاخ 2 لتر نقي مع ملحق',
    'Gas-powered garden plow for soil preparation': 'محراث حديقة يعمل بالغاز',
    'NPK Compound Fertilizer 20-20-20': 'سماد NPK مركب 20-20-20',
    'Organic Compost Fertilizer (5 KG)': 'سماد عضوي (5 كجم)',
    'Urea Fertilizer 46% Nitrogen': 'سماد يوريا 46% نيتروجين',
    'BioShield Organic Pesticide Spray': 'بخاخ مبيد عضوي بايو شيلد',
    'FungoClear Fungicide Concentrate': 'مركز مبيد فطري فونجو كلير',
    'Hybrid Tomato Seeds (F1) - 500g': 'بذور طماطم هجينة (F1) - 500 جم',
    'Sunflower Seeds - 1 KG Pack': 'بذور عباد الشمس - 1 كجم',
    'Maize/Corn Hybrid Seeds - 2 KG': 'بذور ذرة هجينة - 2 كجم',
    'Hand Trowel & Transplanter Set': 'طقم أدوات حديقة يدوية',
}

def run_translation_migrations():
    """Update existing database rows with Arabic translations if missing."""
    try:
        # Update Categories
        for cat in Category.query.all():
            if not cat.name_ar and cat.name in ar_cats:
                cat.name_ar = ar_cats[cat.name]
        
        # Update Products
        for p in Product.query.all():
            if not p.name_ar and p.name in ar_products:
                p.name_ar = ar_products[p.name]
                
            # If still no arabic name, provide a fallback to avoid displaying empty space
            if not p.name_ar:
                p.name_ar = p.name
                
            # Set default description_ar if missing
            if not p.description_ar:
                p.description_ar = p.description

        db.session.commit()
        print("Database translation migration applied successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Migration error: {e}")
