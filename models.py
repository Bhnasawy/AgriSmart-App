"""
models.py - SQLAlchemy database models for Agri Smart
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy extension (app bound later via init_app)
db = SQLAlchemy()


# ---------------------------------------------------------------------------
# User Model
# ---------------------------------------------------------------------------
class User(UserMixin, db.Model):
    """Represents a registered user (customer or admin)."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # 'admin' or 'customer'
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    tomato_predictions = db.relationship('TomatoPrediction', backref='user', lazy=True)
    crop_recommendations = db.relationship('CropRecommendation', backref='user', lazy=True)

    def set_password(self, password):
        """Hash and store the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Return True if user has admin role."""
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'


# ---------------------------------------------------------------------------
# Category Model
# ---------------------------------------------------------------------------
class Category(db.Model):
    """Product category (e.g., Fertilizers, Seeds)."""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(100), nullable=True, default='bi-bag')  # Bootstrap icon class

    # Relationships
    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


# ---------------------------------------------------------------------------
# Product Model
# ---------------------------------------------------------------------------
class Product(db.Model):
    """Represents an agricultural product for sale."""

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(500), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_best_seller = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    cart_items = db.relationship('CartItem', backref='product', lazy=True, cascade='all, delete-orphan')

    @property
    def is_available(self):
        """True if product is in stock."""
        return self.stock_quantity > 0

    def __repr__(self):
        return f'<Product {self.name}>'


# ---------------------------------------------------------------------------
# Order Model
# ---------------------------------------------------------------------------
class Order(db.Model):
    """Represents a customer order."""

    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')  # Pending/Confirmed/Shipped/Delivered

    # Billing information stored at time of order
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False, default='Cash On Delivery')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order #{self.id} - {self.status}>'


# ---------------------------------------------------------------------------
# OrderItem Model
# ---------------------------------------------------------------------------
class OrderItem(db.Model):
    """Represents a single line item within an order."""

    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)  # Snapshot of price at time of purchase

    @property
    def subtotal(self):
        """Calculate line total."""
        return self.quantity * self.price_at_purchase

    def __repr__(self):
        return f'<OrderItem order={self.order_id} product={self.product_id}>'


# ---------------------------------------------------------------------------
# CartItem Model
# ---------------------------------------------------------------------------
class CartItem(db.Model):
    """Represents an item in a user's shopping cart."""

    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return f'<CartItem user={self.user_id} product={self.product_id}>'


# ===========================================================================
# AI / MACHINE LEARNING MODELS
# ===========================================================================

# ---------------------------------------------------------------------------
# DiseaseTreatment Model
# ---------------------------------------------------------------------------
class DiseaseTreatment(db.Model):
    """Stores treatment information for tomato diseases."""

    __tablename__ = 'disease_treatments'

    id = db.Column(db.Integer, primary_key=True)
    disease_name = db.Column(db.String(200), unique=True, nullable=False)
    disease_display_name = db.Column(db.String(200), nullable=True)
    treatment = db.Column(db.Text, nullable=False)
    pesticide = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DiseaseTreatment {self.disease_name}>'


# ---------------------------------------------------------------------------
# TomatoPrediction Model
# ---------------------------------------------------------------------------
class TomatoPrediction(db.Model):
    """Stores history of tomato leaf disease predictions."""

    __tablename__ = 'tomato_predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null if guest
    guest_id = db.Column(db.String(100), nullable=True)   # Session-based ID for guests
    ip_address = db.Column(db.String(50), nullable=True)
    image_filename = db.Column(db.String(300), nullable=True)
    disease_name = db.Column(db.String(200), nullable=False)
    disease_display_name = db.Column(db.String(200), nullable=True)
    confidence = db.Column(db.Float, nullable=False)
    treatment = db.Column(db.Text, nullable=True)
    pesticide = db.Column(db.Text, nullable=True)
    is_healthy = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TomatoPrediction {self.disease_name} {self.confidence:.1f}%>'


# ---------------------------------------------------------------------------
# CropRecommendation Model
# ---------------------------------------------------------------------------
class CropRecommendation(db.Model):
    """Stores history of crop recommendation predictions."""

    __tablename__ = 'crop_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null if guest
    guest_id = db.Column(db.String(100), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    nitrogen = db.Column(db.Float, nullable=False)
    phosphorus = db.Column(db.Float, nullable=False)
    potassium = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    ph = db.Column(db.Float, nullable=False)
    rainfall = db.Column(db.Float, nullable=False)
    recommended_crop = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CropRecommendation {self.recommended_crop}>'
