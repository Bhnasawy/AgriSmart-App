"""
routes.py - All Flask route handlers for AgriSmart
Includes: E-Commerce, Authentication, Admin, and AI/ML routes
"""

import os
from functools import wraps
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, session, jsonify, abort, current_app)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import (db, User, Category, Product, Order, OrderItem, CartItem,
                   DiseaseTreatment, TomatoPrediction, CropRecommendation)

# Create main blueprint
main = Blueprint('main', __name__)

# ---------------------------------------------------------------------------
# Helper Decorators & Utilities
# ---------------------------------------------------------------------------

def admin_required(f):
    """Decorator: restrict access to admin users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Check if uploaded file has an allowed extension."""
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def get_cart_count():
    """Return the number of items in the current user's cart."""
    if current_user.is_authenticated:
        return db.session.query(db.func.sum(CartItem.quantity))\
                         .filter_by(user_id=current_user.id).scalar() or 0
    return 0


# Make cart_count available to all templates
from flask import g

def inject_cart_count():
    return dict(cart_count=get_cart_count())


# ===========================================================================
# PUBLIC ROUTES
# ===========================================================================

# ---------------------------------------------------------------------------
# Home Page
# ---------------------------------------------------------------------------
@main.route('/')
def index():
    """Home page with hero, categories, featured and best-selling products."""
    categories = Category.query.all()
    featured = Product.query.filter_by(is_featured=True).limit(8).all()
    best_sellers = Product.query.filter_by(is_best_seller=True).limit(8).all()
    return render_template('index.html',
                           categories=categories,
                           featured=featured,
                           best_sellers=best_sellers)


# ---------------------------------------------------------------------------
# Shop
# ---------------------------------------------------------------------------
@main.route('/shop')
@login_required
def shop():
    """Browse all products with search and category filter."""
    search_query = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    page = request.args.get('page', 1, type=int)

    query = Product.query

    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))

    if category_id:
        query = query.filter_by(category_id=category_id)

    products = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=12)
    categories = Category.query.all()

    return render_template('shop.html',
                           products=products,
                           categories=categories,
                           search_query=search_query,
                           selected_category=category_id)


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------
@main.route('/categories')
@login_required
def categories():
    """Display all product categories."""
    all_categories = Category.query.all()
    return render_template('categories.html', categories=all_categories)


# ---------------------------------------------------------------------------
# Product Detail
# ---------------------------------------------------------------------------
@main.route('/product/<int:product_id>')
@login_required
def product_detail(product_id):
    """Show full product details page."""
    product = Product.query.get_or_404(product_id)
    related = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(4).all()
    return render_template('product_detail.html', product=product, related=related)


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------
@main.route('/cart')
@login_required
def cart():
    """Display the user's shopping cart."""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)


@main.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Add a product to the cart or increment its quantity."""
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))

    if not product.is_available:
        flash('Sorry, this product is out of stock.', 'danger')
        return redirect(url_for('main.product_detail', product_id=product_id))

    existing = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing:
        existing.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    flash(f'"{product.name}" added to your cart!', 'success')
    return redirect(url_for('main.cart'))


@main.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required
def api_add_to_cart(product_id):
    """AJAX-friendly add-to-cart: returns JSON instead of redirecting."""
    product = Product.query.get_or_404(product_id)
    if not product.is_available:
        return jsonify({'success': False, 'error': 'Product is out of stock.'}), 400

    quantity = int(request.form.get('quantity', 1) if request.form else
                   (request.json.get('quantity', 1) if request.is_json else 1))

    existing = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing:
        existing.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    new_count = get_cart_count()
    return jsonify({
        'success': True,
        'message': f'"{product.name}" added to your cart!',
        'cart_count': new_count
    })

@main.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    """Update the quantity of a cart item."""
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        abort(403)

    quantity = int(request.form.get('quantity', 1))
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity

    db.session.commit()
    flash('Cart updated.', 'success')
    return redirect(url_for('main.cart'))


@main.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    """Remove an item from the cart."""
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        abort(403)

    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('main.cart'))


# ---------------------------------------------------------------------------
# Checkout
# ---------------------------------------------------------------------------
@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page: billing info + payment method."""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash('Your cart is empty. Please add products first.', 'warning')
        return redirect(url_for('main.shop'))

    total = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        payment_method = request.form.get('payment_method', 'Cash On Delivery')

        # Basic validation
        if not all([full_name, email, phone, address]):
            flash('Please fill in all billing information fields.', 'danger')
            return render_template('checkout.html', cart_items=cart_items, total=total)

        # Create the order
        order = Order(
            user_id=current_user.id,
            total_price=total,
            status='Pending',
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            payment_method=payment_method
        )
        db.session.add(order)
        db.session.flush()  # Get order.id before commit

        # Create order items and reduce stock
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.product.price
            )
            db.session.add(order_item)
            # Reduce stock
            cart_item.product.stock_quantity = max(0, cart_item.product.stock_quantity - cart_item.quantity)

        # Clear the cart
        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        flash('Order placed successfully!', 'success')
        return redirect(url_for('main.order_success', order_id=order.id))

    return render_template('checkout.html', cart_items=cart_items, total=total)


# ---------------------------------------------------------------------------
# Order Success
# ---------------------------------------------------------------------------
@main.route('/order-success/<int:order_id>')
@login_required
def order_success(order_id):
    """Show order confirmation page."""
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    return render_template('order_success.html', order=order)


# ---------------------------------------------------------------------------
# Auth: Register
# ---------------------------------------------------------------------------
@main.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        # Validation
        if not all([username, email, password, confirm]):
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already taken. Please choose another.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login.', 'danger')
            return render_template('register.html')

        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f'Welcome to Agri Smart, {username}! Your account has been created.', 'success')
        return redirect(url_for('main.index'))

    return render_template('register.html')


# ---------------------------------------------------------------------------
# Auth: Login
# ---------------------------------------------------------------------------
@main.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')


# ---------------------------------------------------------------------------
# Auth: Logout
# ---------------------------------------------------------------------------
@main.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------
@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and edit user profile."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Check uniqueness
        if username != current_user.username:
            if User.query.filter_by(username=username).first():
                flash('Username already taken.', 'danger')
                return render_template('profile.html')

        if email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('Email already in use.', 'danger')
                return render_template('profile.html')

        current_user.username = username
        current_user.email = email
        current_user.phone = phone
        current_user.address = address

        if new_password:
            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return render_template('profile.html')
            if len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return render_template('profile.html')
            current_user.set_password(new_password)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))

    return render_template('profile.html')


# ---------------------------------------------------------------------------
# My Orders
# ---------------------------------------------------------------------------
@main.route('/my-orders')
@login_required
def my_orders():
    """Show the current user's order history."""
    orders = Order.query.filter_by(user_id=current_user.id)\
                        .order_by(Order.created_at.desc()).all()
    return render_template('my_orders.html', orders=orders)


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------
@main.route('/about')
@login_required
def about():
    return render_template('about.html')


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------
@main.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        flash('Thank you for your message! We will get back to you shortly.', 'success')
        return redirect(url_for('main.contact'))
    return render_template('contact.html')


# ===========================================================================
# ADMIN ROUTES
# ===========================================================================

# ---------------------------------------------------------------------------
# Admin: Dashboard
# ---------------------------------------------------------------------------
@main.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard with key metrics."""
    from datetime import datetime, date
    
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_price)).scalar() or 0
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    low_stock = Product.query.filter(Product.stock_quantity < 10).all()

    # AI Stats
    today = date.today()
    total_tomato = TomatoPrediction.query.count()
    tomato_today = TomatoPrediction.query.filter(db.func.date(TomatoPrediction.created_at) == today).count()
    
    total_crop = CropRecommendation.query.count()
    crop_today = CropRecommendation.query.filter(db.func.date(CropRecommendation.created_at) == today).count()
    
    # Most predicted disease
    most_pred_disease_row = db.session.query(
        TomatoPrediction.disease_display_name, db.func.count(TomatoPrediction.id).label('total')
    ).group_by(TomatoPrediction.disease_display_name).order_by(db.text('total DESC')).first()
    most_pred_disease = most_pred_disease_row.disease_display_name if most_pred_disease_row else 'N/A'

    # Most recommended crop
    most_rec_crop_row = db.session.query(
        CropRecommendation.recommended_crop, db.func.count(CropRecommendation.id).label('total')
    ).group_by(CropRecommendation.recommended_crop).order_by(db.text('total DESC')).first()
    most_rec_crop = most_rec_crop_row.recommended_crop.title() if most_rec_crop_row else 'N/A'

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_products=total_products,
                           total_orders=total_orders,
                           total_revenue=total_revenue,
                           recent_orders=recent_orders,
                           low_stock=low_stock,
                           total_tomato=total_tomato,
                           tomato_today=tomato_today,
                           total_crop=total_crop,
                           crop_today=crop_today,
                           most_pred_disease=most_pred_disease,
                           most_rec_crop=most_rec_crop)


# ---------------------------------------------------------------------------
# Admin: Manage Products
# ---------------------------------------------------------------------------
@main.route('/admin/products')
@login_required
@admin_required
def admin_products():
    """List all products for admin management."""
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products)


@main.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_product():
    """Add a new product."""
    categories = Category.query.all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        name_ar = request.form.get('name_ar', '').strip()
        description = request.form.get('description', '').strip()
        description_ar = request.form.get('description_ar', '').strip()
        price = float(request.form.get('price', 0))
        stock_quantity = int(request.form.get('stock_quantity', 0))
        category_id = int(request.form.get('category_id', 0))
        is_featured = bool(request.form.get('is_featured'))
        is_best_seller = bool(request.form.get('is_best_seller'))
        image_url = request.form.get('image_url', '').strip()

        # Handle file upload
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_path = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_path, exist_ok=True)
                file.save(os.path.join(upload_path, filename))
                image_url = f'/uploads/{filename}'

        product = Product(
            name=name,
            name_ar=name_ar,
            description=description,
            description_ar=description_ar,
            price=price,
            stock_quantity=stock_quantity,
            category_id=category_id,
            is_featured=is_featured,
            is_best_seller=is_best_seller,
            image_url=image_url or None
        )
        db.session.add(product)
        db.session.commit()
        flash(f'Product "{name}" added successfully!', 'success')
        return redirect(url_for('main.admin_products'))

    return render_template('admin/product_form.html', categories=categories, product=None)


@main.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_product(product_id):
    """Edit an existing product."""
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()

    if request.method == 'POST':
        product.name = request.form.get('name', '').strip()
        product.name_ar = request.form.get('name_ar', '').strip()
        product.description = request.form.get('description', '').strip()
        product.description_ar = request.form.get('description_ar', '').strip()
        product.price = float(request.form.get('price', 0))
        product.stock_quantity = int(request.form.get('stock_quantity', 0))
        product.category_id = int(request.form.get('category_id', 0))
        product.is_featured = bool(request.form.get('is_featured'))
        product.is_best_seller = bool(request.form.get('is_best_seller'))
        image_url = request.form.get('image_url', '').strip()

        # Handle file upload
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_path = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_path, exist_ok=True)
                file.save(os.path.join(upload_path, filename))
                image_url = f'/uploads/{filename}'

        if image_url:
            product.image_url = image_url

        db.session.commit()
        flash(f'Product "{product.name}" updated successfully!', 'success')
        return redirect(url_for('main.admin_products'))

    return render_template('admin/product_form.html', categories=categories, product=product)


@main.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_product(product_id):
    """Delete a product."""
    product = Product.query.get_or_404(product_id)
    name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{name}" deleted.', 'info')
    return redirect(url_for('main.admin_products'))


# ---------------------------------------------------------------------------
# Admin: Manage Categories
# ---------------------------------------------------------------------------
@main.route('/admin/categories')
@login_required
@admin_required
def admin_categories():
    """List all categories."""
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)


@main.route('/admin/categories/add', methods=['POST'])
@login_required
@admin_required
def admin_add_category():
    """Add a new category."""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    icon = request.form.get('icon', 'bi-bag').strip()

    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('main.admin_categories'))

    if Category.query.filter_by(name=name).first():
        flash('Category already exists.', 'danger')
        return redirect(url_for('main.admin_categories'))

    category = Category(name=name, description=description, icon=icon)
    db.session.add(category)
    db.session.commit()
    flash(f'Category "{name}" added!', 'success')
    return redirect(url_for('main.admin_categories'))


@main.route('/admin/categories/edit/<int:cat_id>', methods=['POST'])
@login_required
@admin_required
def admin_edit_category(cat_id):
    """Edit a category."""
    category = Category.query.get_or_404(cat_id)
    category.name = request.form.get('name', '').strip()
    category.description = request.form.get('description', '').strip()
    category.icon = request.form.get('icon', 'bi-bag').strip()
    db.session.commit()
    flash(f'Category "{category.name}" updated!', 'success')
    return redirect(url_for('main.admin_categories'))


@main.route('/admin/categories/delete/<int:cat_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_category(cat_id):
    """Delete a category (only if it has no products)."""
    category = Category.query.get_or_404(cat_id)
    if category.products:
        flash('Cannot delete category that has products. Remove products first.', 'danger')
        return redirect(url_for('main.admin_categories'))

    name = category.name
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{name}" deleted.', 'info')
    return redirect(url_for('main.admin_categories'))


# ---------------------------------------------------------------------------
# Admin: Manage Orders
# ---------------------------------------------------------------------------
@main.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    """View all orders."""
    status_filter = request.args.get('status', '')
    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    orders = query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)


@main.route('/admin/orders/update-status/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def admin_update_order_status(order_id):
    """Update the status of an order."""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status', 'Pending')
    valid_statuses = ['Pending', 'Confirmed', 'Shipped', 'Delivered']
    if new_status in valid_statuses:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.id} status updated to "{new_status}".', 'success')
    else:
        flash('Invalid status.', 'danger')
    return redirect(url_for('main.admin_orders'))

@main.route('/admin/orders/delete/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_order(order_id):
    """Delete an order and its items."""
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash(f'Order #{order.id} has been deleted.', 'success')
    return redirect(url_for('main.admin_orders'))


# ---------------------------------------------------------------------------
# Admin: Manage Users
# ---------------------------------------------------------------------------
@main.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """View all registered users."""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


# ---------------------------------------------------------------------------
# Serve uploaded files
# ---------------------------------------------------------------------------
from flask import send_from_directory

@main.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve files from the uploads directory."""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


# ===========================================================================
# AI / MACHINE LEARNING ROUTES
# ===========================================================================

import io
import csv
import uuid
import logging
import numpy as np
import requests as http_requests

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pesticide ↔ Product Smart Matching
# ---------------------------------------------------------------------------

# Maps each canonical pesticide keyword to a list of aliases / trade-name
# fragments so that "Mancozeb" matches "MANZEB 75% WP", etc.
# Extend this dict whenever new pesticides or products are added.
PESTICIDE_ALIASES = {
    'mancozeb':           ['mancozeb', 'manzeb', 'dithane', 'manzate'],
    'chlorothalonil':     ['chlorothalonil', 'daconil', 'bravo'],
    'azoxystrobin':       ['azoxystrobin', 'amistar', 'quadris'],
    'copper hydroxide':   ['copper hydroxide', 'kocide', 'champ'],
    'copper oxychloride': ['copper oxychloride', 'coc', 'cupravit'],
    'metalaxyl':          ['metalaxyl', 'ridomil', 'apron'],
    'cymoxanil':          ['cymoxanil', 'curzate'],
    'propiconazole':      ['propiconazole', 'tilt', 'bumper'],
    'difenoconazole':     ['difenoconazole', 'score', 'dividend'],
    'tebuconazole':       ['tebuconazole', 'folicur', 'raxil'],
    'carbendazim':        ['carbendazim', 'bavistin', 'derosal'],
    'thiophanate-methyl': ['thiophanate-methyl', 'thiophanate', 'topsin'],
    'sulfur':             ['sulfur', 'sulphur', 'kumulus', 'microthiol'],
    'abamectin':          ['abamectin', 'vertimec', 'agrimek'],
    'imidacloprid':       ['imidacloprid', 'confidor', 'admire', 'gaucho'],
    'thiamethoxam':       ['thiamethoxam', 'actara', 'cruiser'],
    'lambda-cyhalothrin': ['lambda-cyhalothrin', 'karate', 'warrior'],
    'spiromesifen':       ['spiromesifen', 'oberon'],
    'pyriproxyfen':       ['pyriproxyfen', 'admiral'],
    'neem oil':           ['neem oil', 'neem', 'azadirachtin'],
    'bacillus thuringiensis': ['bacillus thuringiensis', 'bt', 'dipel'],
    'copper sulfate':     ['copper sulfate', 'copper sulphate', 'bordeaux'],
    'mandipropamid':      ['mandipropamid', 'revus'],
    'dimethomorph':       ['dimethomorph', 'acrobat'],
    'famoxadone':         ['famoxadone', 'tanos'],
    'pyrethrin':          ['pyrethrin', 'pyrethrum', 'pyrethrins'],
    'bifenthrin':         ['bifenthrin', 'talstar'],
    'hexythiazox':        ['hexythiazox', 'savey'],
    'dicofol':            ['dicofol', 'kelthane'],
    'propargite':         ['propargite', 'omite'],
    'fenpyroximate':      ['fenpyroximate', 'portal'],
}


def find_matching_products(pesticide_text):
    """
    Given a raw pesticide text string (e.g. "Mancozeb, Chlorothalonil, or
    Azoxystrobin"), find all Product rows whose names partially match any of
    the suggested pesticide keywords or their aliases.

    Returns a list of product dicts ready for JSON serialisation.
    """
    if not pesticide_text:
        return []

    # ── 1. Parse individual pesticide names from the text ──────────────
    # Typical formats: "A, B, or C"  /  "A, B, and C"  /  "A or B"
    import re
    raw = pesticide_text.replace(' or ', ', ').replace(' and ', ', ')
    raw = raw.rstrip('.')
    names = [n.strip().lower() for n in re.split(r'[,;]+', raw) if n.strip()]

    # ── 2. Build the full set of search fragments ──────────────────────
    search_fragments = set()
    for name in names:
        search_fragments.add(name)
        # Also add aliases from the mapping
        for canonical, aliases in PESTICIDE_ALIASES.items():
            # Check if the parsed name matches the canonical key OR any alias
            if name in aliases or canonical in name or name in canonical:
                search_fragments.update(aliases)

    if not search_fragments:
        return []

    # ── 3. Query products using LIKE for each fragment ─────────────────
    from sqlalchemy import or_
    conditions = []
    for fragment in search_fragments:
        conditions.append(Product.name.ilike(f'%{fragment}%'))
        conditions.append(Product.description.ilike(f'%{fragment}%'))

    matched_products = Product.query.join(Category).filter(
        Category.name.ilike('%Pesticide%'),
        or_(*conditions)
    ).all()

    # Deduplicate by product id (a product might match multiple fragments)
    seen_ids = set()
    unique_products = []
    for p in matched_products:
        if p.id not in seen_ids:
            seen_ids.add(p.id)
            unique_products.append(p)

    # ── 4. Serialise for JSON response ─────────────────────────────────
    result = []
    for p in unique_products:
        result.append({
            'id':             p.id,
            'name':           p.name,
            'price':          p.price,
            'image_url':      p.image_url or '',
            'stock_quantity': p.stock_quantity,
            'is_available':   p.is_available,
            'category_name':  p.category.name if p.category else '',
            'category_icon':  p.category.icon if p.category else 'bi-bag',
            'is_featured':    p.is_featured,
            'is_best_seller': p.is_best_seller,
        })

    return result


# Tomato classes & display names (must match ml_loader)
TOMATO_CLASSES = [
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

TOMATO_DISEASE_DISPLAY = {
    "Tomato___Bacterial_spot": "Bacterial Spot",
    "Tomato___Early_blight": "Early Blight",
    "Tomato___Late_blight": "Late Blight",
    "Tomato___Leaf_Mold": "Leaf Mold",
    "Tomato___Septoria_leaf_spot": "Septoria Leaf Spot",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Spider Mites",
    "Tomato___Target_Spot": "Target Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Yellow Leaf Curl Virus",
    "Tomato___Tomato_mosaic_virus": "Tomato Mosaic Virus",
    "Tomato___healthy": "Healthy Leaf",
}

CROP_MAPPING = {
    1: "rice", 2: "maize", 3: "chickpea", 4: "kidneybeans",
    5: "pigeonpeas", 6: "mothbeans", 7: "mungbean", 8: "blackgram",
    9: "lentil", 10: "pomegranate", 11: "banana", 12: "mango",
    13: "grapes", 14: "watermelon", 15: "muskmelon", 16: "apple",
    17: "orange", 18: "papaya", 19: "coconut", 20: "cotton",
    21: "jute", 22: "coffee",
}


def _get_guest_id():
    """Get or create an anonymous guest session ID."""
    if 'guest_id' not in session:
        session['guest_id'] = str(uuid.uuid4())
    return session['guest_id']


def _get_ip():
    """Get the client IP address."""
    return request.headers.get('X-Forwarded-For', request.remote_addr)


# ---------------------------------------------------------------------------
# AI Page Routes
# ---------------------------------------------------------------------------

@main.route('/ai/tomato')
@login_required
def ai_tomato():
    """Tomato Leaf Disease Diagnosis page."""
    return render_template('ai/tomato.html')


@main.route('/ai/crop')
@login_required
def ai_crop():
    """Crop Recommendation System page."""
    return render_template('ai/crop.html')


# ---------------------------------------------------------------------------
# Weather API Proxy (for Crop Recommendation autofill)
# ---------------------------------------------------------------------------

@main.route('/weather/<city>')
@login_required
def get_weather(city):
    """Proxy weather API for crop recommendation weather autofill."""
    if not city or not city.strip():
        return jsonify({'error': 'City name is required'}), 400
    try:
        params = {
            'key': current_app.config.get('WEATHER_API_KEY', ''),
            'q': city.strip()
        }
        resp = http_requests.get(
            current_app.config.get('WEATHER_API_URL', 'https://api.weatherapi.com/v1/current.json'),
            params=params, timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            return jsonify({
                'temperature': data['current'].get('temp_c'),
                'humidity': data['current'].get('humidity')
            })
        elif resp.status_code == 400:
            err = resp.json().get('error', {}).get('message', 'City not found.')
            return jsonify({'error': err}), 400
        else:
            return jsonify({'error': 'Failed to retrieve weather data.'}), 502
    except http_requests.exceptions.Timeout:
        return jsonify({'error': 'Weather service timed out.'}), 504
    except Exception as e:
        logger.error(f'Weather API error: {e}')
        return jsonify({'error': 'Internal server error.'}), 500


# ---------------------------------------------------------------------------
# AI Prediction APIs
# ---------------------------------------------------------------------------

@main.route('/api/tomato/predict', methods=['POST'])
@login_required
def api_tomato_predict():
    """Tomato leaf disease prediction endpoint."""
    tomato_interpreter = getattr(current_app, 'tomato_interpreter', None)
    if tomato_interpreter is None:
        return jsonify({'error': 'Tomato model is not loaded. Please contact the administrator.'}), 500

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request.'}), 400
    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload PNG, JPG, JPEG, GIF, BMP, or WEBP.'}), 400

    filename = secure_filename(file.filename)
    upload_path = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_path, filename)
    file.save(file_path)

    try:
        # Load and preprocess image using Pillow
        from PIL import Image
        img = Image.open(file_path).resize((224, 224))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_array = np.array(img, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Run prediction using TFLite interpreter
        input_details = tomato_interpreter.get_input_details()
        output_details = tomato_interpreter.get_output_details()

        tomato_interpreter.set_tensor(input_details[0]['index'], img_array)
        tomato_interpreter.invoke()
        predictions = tomato_interpreter.get_tensor(output_details[0]['index'])[0]

        predicted_index = int(np.argmax(predictions))
        predicted_class = TOMATO_CLASSES[predicted_index]
        confidence = float(predictions[predicted_index] * 100)
        display_name = TOMATO_DISEASE_DISPLAY.get(predicted_class, predicted_class)
        is_healthy = predicted_class == 'Tomato___healthy'

        # Get treatment from database
        treatment_record = DiseaseTreatment.query.filter_by(disease_name=predicted_class).first()
        treatment_text = treatment_record.treatment if treatment_record else 'Treatment information not available.'
        pesticide_text = treatment_record.pesticide if treatment_record else ''

        # Log prediction to database
        user_id = current_user.id if current_user.is_authenticated else None
        guest_id = None if current_user.is_authenticated else _get_guest_id()
        pred_record = TomatoPrediction(
            user_id=user_id,
            guest_id=guest_id,
            ip_address=_get_ip(),
            image_filename=filename,
            disease_name=predicted_class,
            disease_display_name=display_name,
            confidence=round(confidence, 2),
            treatment=treatment_text,
            pesticide=pesticide_text,
            is_healthy=is_healthy
        )
        db.session.add(pred_record)
        db.session.commit()

        # Find matching products from the store
        recommended_products = find_matching_products(pesticide_text) if not is_healthy else []

        return jsonify({
            'success': True,
            'disease': predicted_class,
            'disease_display': display_name,
            'confidence': round(confidence, 2),
            'treatment': treatment_text,
            'pesticide': pesticide_text,
            'is_healthy': is_healthy,
            'recommended_products': recommended_products
        })
    except Exception as e:
        logger.error(f'Tomato prediction error: {e}')
        return jsonify({'error': 'Prediction failed. Please try again.'}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@main.route('/api/crop/predict', methods=['POST'])
@login_required
def api_crop_predict():
    """Crop recommendation prediction endpoint."""
    crop_model  = getattr(current_app, 'crop_model', None)
    crop_scaler = getattr(current_app, 'crop_scaler', None)

    if crop_model is None or crop_scaler is None:
        return jsonify({'error': 'Crop model is not loaded. Please contact the administrator.'}), 500

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request. JSON body required.'}), 400

    required = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        N           = float(data['N'])
        P           = float(data['P'])
        K           = float(data['K'])
        temperature = float(data['temperature'])
        humidity    = float(data['humidity'])
        ph          = float(data['ph'])
        rainfall    = float(data['rainfall'])
    except (ValueError, TypeError):
        return jsonify({'error': 'All fields must be valid numeric values.'}), 400

    if any(v < 0 for v in [N, P, K, humidity, rainfall]):
        return jsonify({'error': 'Values cannot be negative.'}), 400
    if not (0 <= ph <= 14):
        return jsonify({'error': 'pH must be between 0 and 14.'}), 400
    if not (0 <= humidity <= 100):
        return jsonify({'error': 'Humidity must be between 0 and 100.'}), 400

    try:
        import numpy as np
        import warnings
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            scaled = crop_scaler.transform(input_data)
            pred_class = int(crop_model.predict(scaled)[0])
            
        crop_name = CROP_MAPPING.get(pred_class, 'unknown')

        confidence = None
        if hasattr(crop_model, 'predict_proba'):
            proba = crop_model.predict_proba(scaled)[0]
            confidence = float(np.max(proba))

        # Log recommendation
        user_id = current_user.id if current_user.is_authenticated else None
        guest_id = None if current_user.is_authenticated else _get_guest_id()
        rec = CropRecommendation(
            user_id=user_id,
            guest_id=guest_id,
            ip_address=_get_ip(),
            nitrogen=N, phosphorus=P, potassium=K,
            temperature=temperature, humidity=humidity,
            ph=ph, rainfall=rainfall,
            recommended_crop=crop_name,
            confidence=round(confidence, 4) if confidence else None
        )
        db.session.add(rec)
        db.session.commit()

        payload = {'crop': crop_name}
        if confidence is not None:
            payload['confidence'] = round(confidence, 4)
        return jsonify(payload)

    except Exception as e:
        logger.error(f'Crop prediction error: {e}')
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500


# ===========================================================================
# ADMIN – AI MANAGEMENT ROUTES
# ===========================================================================

# ---------------------------------------------------------------------------
# Admin: Tomato Prediction History
# ---------------------------------------------------------------------------

@main.route('/admin/ai/tomato-predictions')
@login_required
@admin_required
def admin_ai_tomato():
    """View all tomato disease prediction records."""
    search = request.args.get('q', '').strip()
    filter_disease = request.args.get('disease', '').strip()

    query = TomatoPrediction.query
    if search:
        query = query.filter(
            db.or_(
                TomatoPrediction.disease_display_name.ilike(f'%{search}%'),
                TomatoPrediction.ip_address.ilike(f'%{search}%')
            )
        )
    if filter_disease:
        query = query.filter_by(disease_name=filter_disease)

    predictions = query.order_by(TomatoPrediction.created_at.desc()).all()
    all_diseases = db.session.query(TomatoPrediction.disease_name).distinct().all()
    all_diseases = [d[0] for d in all_diseases]

    return render_template('admin/ai_tomato.html',
                           predictions=predictions,
                           all_diseases=all_diseases,
                           search=search,
                           filter_disease=filter_disease)


@main.route('/admin/ai/tomato-predictions/delete/<int:pred_id>', methods=['POST'])
@login_required
@admin_required
def admin_ai_tomato_delete(pred_id):
    pred = TomatoPrediction.query.get_or_404(pred_id)
    db.session.delete(pred)
    db.session.commit()
    flash('Prediction record deleted.', 'info')
    return redirect(url_for('main.admin_ai_tomato'))


@main.route('/admin/ai/tomato-predictions/export')
@login_required
@admin_required
def admin_ai_tomato_export():
    """Export tomato prediction history as CSV."""
    from flask import Response
    predictions = TomatoPrediction.query.order_by(TomatoPrediction.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Date', 'User', 'Guest ID', 'IP', 'Disease', 'Display Name', 'Confidence (%)', 'Is Healthy', 'Treatment'])
    for p in predictions:
        writer.writerow([
            p.id,
            p.created_at.strftime('%Y-%m-%d %H:%M'),
            p.user.username if p.user else 'Guest',
            p.guest_id or '',
            p.ip_address or '',
            p.disease_name,
            p.disease_display_name or '',
            p.confidence,
            'Yes' if p.is_healthy else 'No',
            (p.treatment or '').replace('\n', ' | ')
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=tomato_predictions.csv'}
    )


# ---------------------------------------------------------------------------
# Admin: Crop Recommendation History
# ---------------------------------------------------------------------------

@main.route('/admin/ai/crop-recommendations')
@login_required
@admin_required
def admin_ai_crop():
    """View all crop recommendation records."""
    search = request.args.get('q', '').strip()
    filter_crop = request.args.get('crop', '').strip()

    query = CropRecommendation.query
    if search:
        query = query.filter(
            db.or_(
                CropRecommendation.recommended_crop.ilike(f'%{search}%'),
                CropRecommendation.ip_address.ilike(f'%{search}%')
            )
        )
    if filter_crop:
        query = query.filter_by(recommended_crop=filter_crop)

    recommendations = query.order_by(CropRecommendation.created_at.desc()).all()
    all_crops = db.session.query(CropRecommendation.recommended_crop).distinct().all()
    all_crops = [c[0] for c in all_crops]

    return render_template('admin/ai_crop.html',
                           recommendations=recommendations,
                           all_crops=all_crops,
                           search=search,
                           filter_crop=filter_crop)


@main.route('/admin/ai/crop-recommendations/delete/<int:rec_id>', methods=['POST'])
@login_required
@admin_required
def admin_ai_crop_delete(rec_id):
    rec = CropRecommendation.query.get_or_404(rec_id)
    db.session.delete(rec)
    db.session.commit()
    flash('Recommendation record deleted.', 'info')
    return redirect(url_for('main.admin_ai_crop'))


@main.route('/admin/ai/crop-recommendations/export')
@login_required
@admin_required
def admin_ai_crop_export():
    """Export crop recommendation history as CSV."""
    from flask import Response
    recs = CropRecommendation.query.order_by(CropRecommendation.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Date', 'User', 'Guest ID', 'IP', 'N', 'P', 'K', 'Temp', 'Humidity', 'pH', 'Rainfall', 'Recommended Crop', 'Confidence'])
    for r in recs:
        writer.writerow([
            r.id, r.created_at.strftime('%Y-%m-%d %H:%M'),
            r.user.username if r.user else 'Guest',
            r.guest_id or '', r.ip_address or '',
            r.nitrogen, r.phosphorus, r.potassium,
            r.temperature, r.humidity, r.ph, r.rainfall,
            r.recommended_crop,
            f'{r.confidence:.2%}' if r.confidence else 'N/A'
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=crop_recommendations.csv'}
    )


# ---------------------------------------------------------------------------
# Admin: Treatment Management (CRUD)
# ---------------------------------------------------------------------------

@main.route('/admin/ai/treatments')
@login_required
@admin_required
def admin_ai_treatments():
    """Manage disease treatments."""
    treatments = DiseaseTreatment.query.order_by(DiseaseTreatment.disease_display_name).all()
    return render_template('admin/ai_treatments.html', treatments=treatments)


@main.route('/admin/ai/treatments/add', methods=['POST'])
@login_required
@admin_required
def admin_ai_treatment_add():
    disease_name = request.form.get('disease_name', '').strip()
    display_name = request.form.get('disease_display_name', '').strip()
    treatment    = request.form.get('treatment', '').strip()
    pesticide    = request.form.get('pesticide', '').strip()
    notes        = request.form.get('notes', '').strip()

    if not disease_name or not treatment:
        flash('Disease name and treatment are required.', 'danger')
        return redirect(url_for('main.admin_ai_treatments'))

    if DiseaseTreatment.query.filter_by(disease_name=disease_name).first():
        flash('A treatment for this disease already exists.', 'danger')
        return redirect(url_for('main.admin_ai_treatments'))

    t = DiseaseTreatment(disease_name=disease_name, disease_display_name=display_name,
                         treatment=treatment, pesticide=pesticide, notes=notes)
    db.session.add(t)
    db.session.commit()
    flash(f'Treatment for "{display_name or disease_name}" added!', 'success')
    return redirect(url_for('main.admin_ai_treatments'))


@main.route('/admin/ai/treatments/edit/<int:t_id>', methods=['POST'])
@login_required
@admin_required
def admin_ai_treatment_edit(t_id):
    t = DiseaseTreatment.query.get_or_404(t_id)
    t.disease_display_name = request.form.get('disease_display_name', '').strip()
    t.treatment  = request.form.get('treatment', '').strip()
    t.pesticide  = request.form.get('pesticide', '').strip()
    t.notes      = request.form.get('notes', '').strip()
    db.session.commit()
    flash(f'Treatment updated successfully!', 'success')
    return redirect(url_for('main.admin_ai_treatments'))


@main.route('/admin/ai/treatments/delete/<int:t_id>', methods=['POST'])
@login_required
@admin_required
def admin_ai_treatment_delete(t_id):
    t = DiseaseTreatment.query.get_or_404(t_id)
    name = t.disease_display_name or t.disease_name
    db.session.delete(t)
    db.session.commit()
    flash(f'Treatment for "{name}" deleted.', 'info')
    return redirect(url_for('main.admin_ai_treatments'))
