
from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from . import db
from .models import Product, Cart, CartItem, User
from datetime import datetime, timedelta
import stripe

stripe.api_key = 'sk_test_51OGBhdDSuppRFCsUlLBznFly2zODrIJ3xcwMnZJdaJjxfv52madMPX21CEzS6imZzwORxEMBlgiGemstl99w59H900gPMIhKg5'

cart = Blueprint('cart', __name__)


@cart.route('/cart_page')
def cart_page():

    if 'user_id' not in session:
        flash('Debe de iniciar sesión para ver su carrito', category='error')
        return redirect(url_for('auth.login'))

    count = get_cart_items_count(session['user_id'])

    #Si la cuenta de elementos dentro del carrito es 0, entonces se muestra la página de carrito vacío
    if count == 0:
        session['cart_count'] = get_cart_items_count(session['user_id'])
        return render_template('empty_cart.html')

    #Despliega el carrito del usuario activo
    else:
        #Obtiene el carrito junto con los items del carrito del usuario activo
        cart = Cart.query.filter_by(user_id=session['user_id']).first()
        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()

        #Obtiene el precio total del carrito
        total_price = sum([item.product.total_cost * item.quantity for item in cart_items])

        #Renderiza la pagina del carrito y le envia variables para que se puedan mostrar en la página
        session['cart_count'] = get_cart_items_count(session['user_id'])
        return render_template('cart.html', cart=cart, cart_items=cart_items, total_price=total_price)


@cart.route('/add_cart', methods=['GET', 'POST'])
def add_to_cart():
    if 'user_id' not in session:
        flash('Debe de iniciar sesión para añadir artículos al carrito', category='error')
        return redirect(url_for('auth.login'))

    #Obtiene el usuario activo y se asegura de que no sea un admin
    user = User.query.get(session['user_id'])
    if not user:
        flash('Debe de iniciar sesión para añadir artículos al carrito', category='error')
        return redirect(url_for('auth.login'))
    
    elif user.is_admin:
        flash('No se puede añadir artículos al carrito desde una cuenta de administrador', category='error')
        return redirect(url_for('views.admin_page'))
    
    else:
        #Obtiene el id del producto que se desea añadir al carrito por medio del form en la página del producto
        product_id = request.form['product_id']

        #Se asigna el carrito del usuario activo 
        cart = Cart.query.filter_by(user_id=session['user_id']).first()

        #Se asigna a la variable cart_item los items del carrito del usuario activo, filtrado por el id del carrito y el id del producto
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()

        #Se señala a la variable product como el producto que se desea añadir al carrito
        product = Product.query.filter_by(id=product_id).first()

        #Se resta 1 a la cantidad total del producto en la base de datos.
        if product.quantity > 0:
            product.quantity -= 1

            #Si el item no existe en el carrito, se añade
            if cart_item is None:
                cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=1)
                db.session.add(cart_item)

                #Se encarga de reservar tiempo para que la persona concrete la compra
                cart.time_reserved = datetime.now() + timedelta(minutes=20)

            #Si el item ya existe en el carrito, se le suma 1 a la cantidad
            else:
                cart_item.quantity += 1
            
            #Actualiza la base de datos con respecto al carrito de compras
            db.session.commit()

            flash('Producto correctamente añadido', category='success')
        
        else:
            flash('Producto agotado', category='error')

        #Actualiza el contador del carrito
        count = get_cart_items_count(session['user_id'])
        session['cart_count'] = count

        #Devuelve al usuario a la página de donde vino
        return redirect(request.referrer)
                                             
@cart.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    
    if 'user_id' not in session:
        flash('Debe de iniciar sesión para actualizar el carrito', category='error')
        return redirect(url_for('auth.login'))
    
    # Se filtran los items del carrito por el id del usuario
    cart = Cart.query.filter_by(user_id=session['user_id']).first()
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()

    if item is None:
        flash("El producto no se encuentra en el carrito", category='error')
        return redirect(url_for('views.home'))

    # Obtiene los datos del producto que se desea cambiar
    product = Product.query.get(product_id)

    # Obtiene la cantidad actual del elemento en el carrito.
    old_quantity = item.quantity

    # Obtiene la nueva cantidad tomada que se quiere tener en el carrito por medio del form en la página del carrito
    new_quantity = int(request.form.get('quantity'))


    # calcula la diferencia entre la cantidad nueva y la vieja
    quantity_difference = new_quantity - old_quantity

    # Permite que se pueda actualizar el carrito con una cantidad apropiada. Si el usuario desea aumentar su cantidad pero otro usuario ya obtuvo el stock, no permite que aumente la cantidad.
    if quantity_difference > product.quantity:
        flash('La cantidad seleccionada excede la cantidad disponible del producto', category='error')
        return redirect(request.referrer)
    
    # Actualiza la cantidad del item en el carrito y en el stock
    item.quantity = new_quantity
    product.quantity -= quantity_difference

    # Actualiza la base de datos
    db.session.commit()

    #Actualiza carrito arriba
    session['cart_count'] = get_cart_items_count(session['user_id'])

    # Redirecciona a la pagina de compra
    return redirect(url_for('cart.cart_page'))

@cart.route('delete_item/<int:product_id>', methods=['POST'])
def remove_item(product_id):

    if 'user_id' not in session:
        flash('Debe de iniciar sesión para eliminar artículos del carrito', category='error')
        return redirect(url_for('auth.login'))

    #Recupera el item del carrito
    item = CartItem.query.filter_by(product_id=product_id).first()

    if item is None:
        flash('El producto no se encuentra en el carrito', category='error')
        return redirect(url_for('views.home'))

    #Recupera la cantidad del item al stock
    product = Product.query.get(product_id)
    product.quantity += item.quantity

    #Borra el item del carrito
    db.session.delete(item)

    #Actualiza la base de datos de carrito
    db.session.commit()

    session['cart_count'] = get_cart_items_count(session['user_id'])

    return redirect(url_for('cart.cart_page'))

@cart.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        flash('Debe de iniciar sesión para realizar el pago', category='error')
        return redirect(url_for('auth.login'))
    
    cart = Cart.query.filter_by(user_id=session['user_id']).first()
    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()

    if not cart_items:
        flash('No hay artículos en el carrito', category='error')
        return redirect(url_for('views.home'))

    total_price = sum([item.product.total_cost * item.quantity for item in cart_items])

    #Crea la sesión de checkout de Stripe
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types = ['card'],
            line_items=[{
                'price_data': {
                    'currency': 'crc',
                    'product_data': {
                        'name': 'Compra de carne',
                    },
                    'unit_amount': int(total_price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('cart.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('cart.cancel', _external=True),
        )
    except Exception as e:
        flash('Error al crear la sesión de pago de Stripe: {}'.format(str(e)), category='error')
        return redirect(url_for('cart.cart_page'))
    
    return redirect(checkout_session.url, code=303)

@cart.route('/success')
def success():
    flash('Compra exitosa', category='success')
    
    # Obtiene el carrito del usuario activo. Lo filtra por medio del user_id
    user_cart = Cart.query.filter_by(user_id=session['user_id']).first()

    #Si el carrito no está vacío, entonces elimina cada item presente en él.
    if user_cart is not None:
        
        #Borra los elementos del carrito.
        CartItem.query.filter_by(cart_id=user_cart.id).delete()
        db.session.commit()
    else:
        flash('No cart found', category='error')

    session['cart_count'] = get_cart_items_count(session['user_id'])
    return render_template('home.html')

@cart.route('/cancel')
def cancel(): 
    flash('Compra cancelada', category='error')
    return redirect(url_for('cart.cart_page'))

def get_cart_items_count(user_id): #TOMA LA CUENTA DE TODOS LOS ARTICULOS POR USUARIO
    cart = Cart.query.filter_by(user_id=user_id).first()
    if cart is None:
        return 0
    else:

        #sum es una funcion de SQLAlchemy, calcula la suma de la columna
        return db.session.query(db.func.sum(CartItem.quantity)).filter_by(cart_id=cart.id).scalar() or 0
    
def check_cart_reservation():
    carts = Cart.query.all()
    for cart in carts:
        #Si existe cart.time_reserved y es menor a la hora actual, entonces se borra el carrito
        if cart.time_reserved and cart.time_reserved < datetime.now():
            cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
            for item in cart_items:
                product = Product.query.get(item.product_id)
                product.quantity += item.quantity
                db.session.delete(item)
            cart.time_reserved = None
            db.session.commit()

            