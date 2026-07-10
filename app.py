"""
app.py - Flask application factory and entry point for AgriSmart
"""

import os
from flask import Flask, render_template, request, make_response
from flask_login import LoginManager
from config import Config
from models import db, User, Category, Product, DiseaseTreatment


def create_app():
    """Application factory: create and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure the instance folder exists
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
    # Ensure the uploads folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # Ensure the ml_models folder exists (in case someone clones without files)
    os.makedirs(app.config['ML_MODELS_FOLDER'], exist_ok=True)

    # -----------------------------------------------------------------------
    # Initialize extensions
    # -----------------------------------------------------------------------
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'يجب تسجيل الدخول أولاً للوصول إلى هذه الصفحة. | Please log in first to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # -----------------------------------------------------------------------
    # Load Machine Learning models (once at startup)
    # -----------------------------------------------------------------------
    from ml_loader import load_models
    load_models(app)

    # -----------------------------------------------------------------------
    # Register blueprint
    # -----------------------------------------------------------------------
    from routes import main, inject_cart_count
    app.register_blueprint(main)

    # Inject cart count into all templates
    app.context_processor(inject_cart_count)

    # -----------------------------------------------------------------------
    # Inject current language into all templates
    # -----------------------------------------------------------------------
    @app.context_processor
    def inject_lang():
        """Pass the current UI language ('en' or 'ar') to every template."""
        lang = request.cookies.get('agrismart_lang', 'en')
        if lang not in ('en', 'ar'):
            lang = 'en'
        return {'lang': lang}

    # -----------------------------------------------------------------------
    # Language switch route (called by JS fetch)
    # -----------------------------------------------------------------------
    @app.route('/set-lang/<lang>')
    def set_lang(lang):
        """Store language preference in a cookie and redirect back."""
        if lang not in ('en', 'ar'):
            lang = 'en'
        referrer = request.referrer or '/'
        resp = make_response('', 204)   # No-content (JS handles reload)
        resp.set_cookie('agrismart_lang', lang, max_age=60*60*24*365, samesite='Lax')
        return resp

    # -----------------------------------------------------------------------
    # Custom error handlers
    # -----------------------------------------------------------------------
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('404.html', error_code=403,
                               error_msg='You do not have permission to access this page.'), 403

    @app.errorhandler(413)
    def file_too_large(e):
        from flask import jsonify
        return jsonify({'error': 'File is too large. Maximum size is 16 MB.'}), 413

    # -----------------------------------------------------------------------
    # Database initialization & seeding
    # -----------------------------------------------------------------------
    with app.app_context():
        db.create_all()
        
        # --- Automatic DB Migration for new columns ---
        try:
            db.session.execute(db.text("ALTER TABLE categories ADD COLUMN name_ar VARCHAR(100)"))
            db.session.commit()
            print("Added name_ar to categories")
        except Exception:
            db.session.rollback()

        try:
            db.session.execute(db.text("ALTER TABLE products ADD COLUMN name_ar VARCHAR(200)"))
            db.session.commit()
            print("Added name_ar to products")
        except Exception:
            db.session.rollback()

        try:
            db.session.execute(db.text("ALTER TABLE products ADD COLUMN description_ar TEXT"))
            db.session.commit()
            print("Added description_ar to products")
        except Exception:
            db.session.rollback()
        # ----------------------------------------------
        
        # Populate missing Arabic translations for existing rows
        try:
            from db_migration import run_translation_migrations
            run_translation_migrations()
        except ImportError:
            print("Warning: db_migration.py not found.")

        _seed_database()

    return app


def _seed_database():
    """Seed the database with initial categories, admin user, sample products, and AI treatments."""

    # Only seed if the database is empty
    if Category.query.first():
        # Still seed treatments if they don't exist yet (for existing DBs being upgraded)
        _seed_treatments()
        return

    print("Seeding database with initial data...")

    # ------------------------------------------------------------------
    # Seed Categories
    # ------------------------------------------------------------------
    categories_data = [
        {'name': 'Fertilizers',      'description': 'Organic and chemical fertilizers to boost crop yield.',     'icon': 'bi-droplet-fill'},
        {'name': 'Pesticides',        'description': 'Safe and effective pesticides to protect your crops.',       'icon': 'bi-shield-fill'},
        {'name': 'Seeds',             'description': 'High-quality certified seeds for various crops.',            'icon': 'bi-flower1'},
        {'name': 'Farming Tools',     'description': 'Durable hand tools and equipment for every farmer.',        'icon': 'bi-tools'},
        {'name': 'Safety Wearables',  'description': 'Protective gear to keep farmers safe while working.',        'icon': 'bi-person-check-fill'},
        {'name': 'Electronic Devices','description': 'Smart devices and sensors for modern precision farming.',    'icon': 'bi-cpu-fill'},
    ]

    categories = {}
    for data in categories_data:
        cat = Category(**data)
        db.session.add(cat)
        db.session.flush()
        categories[data['name']] = cat

    # ------------------------------------------------------------------
    # Seed Admin User
    # ------------------------------------------------------------------
    admin = User(username='admin', email='admin@agrismart.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)

    # ------------------------------------------------------------------
    # Seed Sample Products
    # ------------------------------------------------------------------
    products_data = [
        # Fertilizers
        {
            'name': 'NPK Compound Fertilizer 20-20-20',
            'description': 'A balanced granular fertilizer providing equal nitrogen, phosphorus, and potassium for all-round crop development. Ideal for vegetables, fruits, and cereals.',
            'price': 25.99, 'stock_quantity': 150,
            'category': 'Fertilizers', 'is_featured': True, 'is_best_seller': True,
            'image_url': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&q=80'
        },
        {
            'name': 'Organic Compost Fertilizer (5 KG)',
            'description': 'Rich organic compost made from natural materials. Improves soil structure, water retention, and microbial activity. 100% chemical-free.',
            'price': 18.50, 'stock_quantity': 200,
            'category': 'Fertilizers', 'is_featured': True, 'is_best_seller': False,
            'image_url': 'https://images.unsplash.com/photo-1595436723143-c03e1c9b9f3a?w=400&q=80'
        },
        {
            'name': 'Urea Fertilizer 46% Nitrogen',
            'description': 'High-nitrogen urea fertilizer promoting fast leafy growth. Suitable for grains, sugarcane, and most field crops.',
            'price': 22.00, 'stock_quantity': 180,
            'category': 'Fertilizers', 'is_featured': False, 'is_best_seller': True,
            'image_url': 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400&q=80'
        },
        # Pesticides
        {
            'name': 'BioShield Organic Pesticide Spray',
            'description': 'Eco-friendly botanical pesticide spray effective against aphids, mites, and whiteflies. Safe for beneficial insects and humans.',
            'price': 14.99, 'stock_quantity': 120,
            'category': 'Pesticides', 'is_featured': True, 'is_best_seller': True,
            'image_url': 'https://images.unsplash.com/photo-1586771107445-d3ca888129ff?w=400&q=80'
        },
        {
            'name': 'FungoClear Fungicide Concentrate',
            'description': 'Broad-spectrum fungicide for controlling powdery mildew, blight, and rust diseases. Systemic action for lasting protection.',
            'price': 19.99, 'stock_quantity': 90,
            'category': 'Pesticides', 'is_featured': False, 'is_best_seller': False,
            'image_url': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&q=80'
        },
        # Seeds
        {
            'name': 'Hybrid Tomato Seeds (F1) - 500g',
            'description': 'High-yield F1 hybrid tomato seeds with disease resistance. Produces large, firm red fruits. Suitable for greenhouse and open-field cultivation.',
            'price': 9.99, 'stock_quantity': 300,
            'category': 'Seeds', 'is_featured': True, 'is_best_seller': True,
            'image_url': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400&q=80'
        },
        {
            'name': 'Sunflower Seeds - 1 KG Pack',
            'description': 'Premium non-GMO sunflower seeds suitable for oil production and snacks. Fast germination rate of 95%.',
            'price': 7.50, 'stock_quantity': 250,
            'category': 'Seeds', 'is_featured': False, 'is_best_seller': True,
            'image_url': 'https://images.unsplash.com/photo-1470509037663-253d2d33b38a?w=400&q=80'
        },
        {
            'name': 'Maize/Corn Hybrid Seeds - 2 KG',
            'description': 'Drought-tolerant hybrid corn seeds with high starch content. Ideal for animal feed and human consumption. Yields up to 8 tons/hectare.',
            'price': 12.00, 'stock_quantity': 200,
            'category': 'Seeds', 'is_featured': True, 'is_best_seller': False,
            'image_url': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400&q=80'
        },
        # Farming Tools
        {
            'name': 'Heavy Duty Garden Shovel',
            'description': 'Premium stainless steel shovel with a comfortable D-grip handle. Ergonomic design reduces fatigue. Suitable for digging, planting, and soil turning.',
            'price': 34.99, 'stock_quantity': 75,
            'category': 'Farming Tools', 'is_featured': True, 'is_best_seller': True,
            'image_url': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&q=80'
        },
        {
            'name': 'Irrigation Drip Kit (100m)',
            'description': 'Complete drip irrigation kit for 100 meters of rows. Includes main pipe, drippers, connectors, and filter. Saves up to 60% water.',
            'price': 89.99, 'stock_quantity': 40,
            'category': 'Farming Tools', 'is_featured': True, 'is_best_seller': True,
            'image_url': 'https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=400&q=80'
        },
        {
            'name': 'Hand Trowel & Transplanter Set',
            'description': 'Set of 3 ergonomic hand tools: trowel, transplanter, and cultivator. Stainless steel heads with anti-slip rubber handles.',
            'price': 16.99, 'stock_quantity': 100,
            'category': 'Farming Tools', 'is_featured': False, 'is_best_seller': False,
            'image_url': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&q=80'
        },
        # Safety Wearables
        {
            'name': 'Chemical-Resistant Farming Gloves',
            'description': 'Heavy-duty nitrile gloves with extended cuff for wrist protection. Resistant to fertilizers, pesticides, and solvents. One size fits most.',
            'price': 11.99, 'stock_quantity': 200,
            'category': 'Safety Wearables', 'is_featured': True, 'is_best_seller': True,
            'image_url': 'https://images.unsplash.com/photo-1559827291-72ee739d0d9a?w=400&q=80'
        },
        {
            'name': 'Agricultural Safety Boot (Size 42)',
            'description': 'Waterproof rubber boots with steel toe cap and anti-slip sole. Perfect for wet field conditions. Available in multiple sizes.',
            'price': 45.00, 'stock_quantity': 60,
            'category': 'Safety Wearables', 'is_featured': False, 'is_best_seller': True,
            'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80'
        },
        {
            'name': 'Respirator Mask for Pesticide Spraying',
            'description': 'Half-face respirator mask with dual P100 filters. Protects against chemical vapors, pesticide mist, and dust particles.',
            'price': 28.50, 'stock_quantity': 80,
            'category': 'Safety Wearables', 'is_featured': False, 'is_best_seller': False,
            'image_url': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400&q=80'
        },
        # Electronic Devices
        {
            'name': 'Soil pH & Moisture Sensor',
            'description': 'Digital 3-in-1 soil tester measuring pH, moisture, and light intensity. No batteries required. Instant readings for optimal crop management.',
            'price': 22.99, 'stock_quantity': 110,
            'category': 'Electronic Devices', 'is_featured': True, 'is_best_seller': True,
            'image_url': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80'
        },
        {
            'name': 'Smart Weather Station for Farm',
            'description': 'Wireless weather station with LCD display. Monitors temperature, humidity, rainfall, wind speed, and UV index. Includes mobile app connectivity.',
            'price': 129.99, 'stock_quantity': 30,
            'category': 'Electronic Devices', 'is_featured': True, 'is_best_seller': False,
            'image_url': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&q=80'
        },
        {
            'name': 'Automatic Plant Watering Timer',
            'description': 'Programmable digital watering timer for garden hoses. Set up to 16 watering cycles per day. Durable, weatherproof casing.',
            'price': 39.99, 'stock_quantity': 55,
            'category': 'Electronic Devices', 'is_featured': False, 'is_best_seller': True,
            'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80'
        },
    ]

    for data in products_data:
        cat_name = data.pop('category')
        product = Product(category_id=categories[cat_name].id, **data)
        db.session.add(product)

    db.session.commit()
    print("Database seeded successfully!")

    # Seed AI treatments
    _seed_treatments()


def _seed_treatments():
    """Seed default disease treatment records if they don't exist."""
    if DiseaseTreatment.query.first():
        return

    print("Seeding disease treatments...")
    treatments_data = [
        {
            'disease_name': 'Tomato___Bacterial_spot',
            'disease_display_name': 'Bacterial Spot',
            'treatment': 'Remove infected leaves immediately. Avoid overhead watering. Rotate crops annually.',
            'pesticide': 'Copper Hydroxide or Copper Oxychloride (Copper-based bactericide).',
            'notes': 'Apply in the early morning. Repeat every 7–10 days during wet conditions.'
        },
        {
            'disease_name': 'Tomato___Early_blight',
            'disease_display_name': 'Early Blight',
            'treatment': 'Remove infected leaves and improve air circulation around plants.',
            'pesticide': 'Mancozeb, Chlorothalonil, or Azoxystrobin.',
            'notes': 'Apply fungicide at first sign of disease. Repeat every 7 days.'
        },
        {
            'disease_name': 'Tomato___Late_blight',
            'disease_display_name': 'Late Blight',
            'treatment': 'Remove and destroy infected plants. Avoid excessive moisture and overhead irrigation.',
            'pesticide': 'Metalaxyl + Mancozeb (Ridomil Gold), Chlorothalonil, or Copper Hydroxide.',
            'notes': 'Late blight spreads rapidly. Act immediately upon detection.'
        },
        {
            'disease_name': 'Tomato___Leaf_Mold',
            'disease_display_name': 'Leaf Mold',
            'treatment': 'Reduce humidity and improve greenhouse ventilation.',
            'pesticide': 'Chlorothalonil, Mancozeb, or Azoxystrobin.',
            'notes': 'Common in greenhouse-grown tomatoes. Maintain humidity below 85%.'
        },
        {
            'disease_name': 'Tomato___Septoria_leaf_spot',
            'disease_display_name': 'Septoria Leaf Spot',
            'treatment': 'Remove infected leaves. Avoid wetting foliage when watering.',
            'pesticide': 'Chlorothalonil, Mancozeb, or Copper Fungicide.',
            'notes': 'Apply mulch to prevent soil splash. Stake plants for better airflow.'
        },
        {
            'disease_name': 'Tomato___Spider_mites Two-spotted_spider_mite',
            'disease_display_name': 'Spider Mites',
            'treatment': 'Remove heavily infested leaves. Monitor plants regularly. Increase humidity.',
            'pesticide': 'Abamectin, Spiromesifen, or Neem Oil (for light infestations).',
            'notes': 'Spider mites thrive in hot, dry conditions. Avoid broad-spectrum insecticides that kill natural predators.'
        },
        {
            'disease_name': 'Tomato___Target_Spot',
            'disease_display_name': 'Target Spot',
            'treatment': 'Improve airflow and avoid overhead irrigation.',
            'pesticide': 'Azoxystrobin, Pyraclostrobin, or Chlorothalonil.',
            'notes': 'Ensure adequate plant spacing for airflow.'
        },
        {
            'disease_name': 'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
            'disease_display_name': 'Yellow Leaf Curl Virus',
            'treatment': 'Remove and destroy infected plants immediately. Use resistant varieties. Control whitefly vectors.',
            'pesticide': 'Imidacloprid or Thiamethoxam to control whiteflies (virus vectors).',
            'notes': 'No direct cure exists. Prevention through vector control is essential.'
        },
        {
            'disease_name': 'Tomato___Tomato_mosaic_virus',
            'disease_display_name': 'Tomato Mosaic Virus',
            'treatment': 'Remove infected plants immediately. Disinfect all gardening tools. Use virus-free seeds.',
            'pesticide': 'No direct chemical cure available. Use virus-resistant varieties.',
            'notes': 'Wash hands thoroughly before handling plants. Virus spreads by contact.'
        },
        {
            'disease_name': 'Tomato___healthy',
            'disease_display_name': 'Healthy Leaf',
            'treatment': 'Continue regular watering and provide sufficient sunlight.',
            'pesticide': 'No pesticide needed. Apply preventive fertilizer as required.',
            'notes': 'Inspect the plant regularly for early signs of pests and diseases.'
        },
    ]

    for data in treatments_data:
        treatment = DiseaseTreatment(**data)
        db.session.add(treatment)

    db.session.commit()
    print("Disease treatments seeded successfully!")


# Create the application instance
app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
