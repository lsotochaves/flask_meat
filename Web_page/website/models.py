from . import db 
from flask_login import UserMixin

# Crea el modelo referente a los productos en la base de datos
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    base_cost_per_kilogram = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

#Crea el modelo referente a los usuarios en la base de datos
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False) #DEBEN SER UNICOS Y NO PUEDE SER UN ESPACIO VACIO
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
# Crea el modelo referente a los carritos en la base de datos
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cart_items = db.relationship('CartItem', backref='cart', lazy=True)
    time_reserved = db.Column(db.DateTime)

# Crea el modelo referente a los items del carrito en la base de datos
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id')) #Crea relacion con la tabla de productos
    product = db.relationship('Product', backref='cart_items') #Accesa a los atributos del producto
    quantity = db.Column(db.Integer, nullable=False)
    

