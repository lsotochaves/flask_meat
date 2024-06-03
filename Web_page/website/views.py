from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from . import db 
from .models import Product, User, Cart, CartItem
from .cart import get_cart_items_count


views = Blueprint('views', __name__)

#Ruta para la página de inicio
@views.route('/')
def home():

    #Si el usuario no está en sesión, se le muestra la página de inicio
    if 'user_id' not in session:
        return render_template('home.html')

    #Si el usuario está en sesión, se le muestra la página de inicio y se actualiza el contador del carrito
    session['cart_count'] = get_cart_items_count(session['user_id'])
    return render_template('home.html')


#Rutas para cada tipo de corte
@views.route('/ribeye')
def ribeye():

    # Obtiene los productos filtrados por nombre y cantidad, ordenados por peso
    products = Product.query.filter(Product.name=='ribeye', Product.quantity>0).order_by(Product.weight).all()
    
    if 'user_id' in session:
        session['cart_count'] = get_cart_items_count(session['user_id'])
    return render_template('ribeye.html', products=products)

@views.route('/t_bone')
def t_bone():

    products = Product.query.filter(Product.name=='t_bone', Product.quantity>0).order_by(Product.weight).all()
    if 'user_id' in session:
        session['cart_count'] = get_cart_items_count(session['user_id'])
    return render_template('t_bone.html', products=products)

@views.route('/nueva_york')
def nueva_york():

    products = Product.query.filter(Product.name=='nueva_york', Product.quantity>0).order_by(Product.weight).all()
    if 'user_id' in session:
        session['cart_count'] = get_cart_items_count(session['user_id'])
    return render_template('nueva_york.html', products=products)

@views.route('/skirt_steak')
def skirt_steak():
      
    products = Product.query.filter(Product.name=='skirt_steak', Product.quantity>0).order_by(Product.weight).all()
    if 'user_id' in session:
        session['cart_count'] = get_cart_items_count(session['user_id'])
    return render_template('skirt_steak.html', products=products)

@views.route('/picanha')
def picanha():

    products = Product.query.filter(Product.name=='picanha', Product.quantity>0).order_by(Product.weight).all()
    if 'user_id' in session:
        session['cart_count'] = get_cart_items_count(session['user_id'])
    return render_template('picanha.html', products=products)

@views.route('/tomahawk')
def tomahawk():
    
    products = Product.query.filter(Product.name=='tomahawk', Product.quantity>0).order_by(Product.weight).all()
    if 'user_id' in session:
        session['cart_count'] = get_cart_items_count(session['user_id'])
    return render_template('tomahawk.html', products=products)

@views.route('/admin')
def admin_page():
    if 'user_id' not in session:
        flash('Debe de iniciar sesión para acceder a esta página', category='error')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        flash('No tiene permiso para acceder a esta página', category='error')
        return redirect(url_for('views.home'))
    
    return render_template('admin.html')

@views.route('/add_stock', methods=['GET', 'POST'])
def add_stock():

    #Se brindan los precios base por kilogramo de los productos
    base_costs = {
        'ribeye': 18000,
        'picanha': 28000,
        'nueva_york': 16000,
        'skirt_steak': 12000,
        't_bone': 26000,
        'tomahawk': 34000
    }

    #Si el usuario no está en la sesión, se le redirige a la página de inicio de sesión
    if 'user_id' not in session:
        flash('Debe de iniciar sesión para acceder a esta página', category='error')
        return redirect(url_for('auth.login'))
    
    #Si el usuario si está en la sesión, se obtiene su id.
    user = User.query.get(session['user_id'])

    #Si el usuario no existe o no es admin, se le notifica que no tiene permiso para acceder a la página
    if not user or not user.is_admin:
        flash('No tiene permiso para acceder a esta página', category='error')
        return redirect(url_for('views.home'))
    
    #Si el usuario indica un método POST, se obtienen los valores escogidos por el usuario.
    if request.method == 'POST':
        name = request.form.get('name')
        weight = request.form.get('weight')  
        quantity = request.form.get('quantity')

        #Si el peso o la cantidad están vacíos, se le notifica al usuario que no puede ingresar un dato vacío
        if weight == '' or quantity == '':
            flash('No se puede ingresar un dato vacío', category='error')
            return redirect(url_for('views.add_stock'))
        
        #Si no son vacíos, se convierten a float y a int respectivamente
        weight = float(weight)
        quantity = int(quantity)

        #Si el usuario ingresa un peso o cantidad negativa, se le notifica que no puede hacerlo
        if weight <= 0 or quantity <= 0:
            flash('No se puede ingresar una cantidad negativa', category='error')
            return redirect(url_for('views.add_stock'))

        #Se busca el producto por nombre y por peso.
        product = Product.query.filter_by(name=name, weight=weight).first()
        
        #Si el producto ya existe, se le notifica al usuario que se añadió la cantidad al producto existente
        if product:
            flash('El producto ya existe en el inventario, por lo que se añadió la cantidad al producto existente', category='success')
            
            #Aumenta la cantidad del producto existente
            product.quantity += quantity
            db.session.commit()
            return render_template('add_stock.html')

        #Si el producto no existe, se crea un nuevo producto
        else:
            #Se compara el nombre del producto con el diccionario de precios base para obtener el precio base por kilogramo
            base_cost_per_kilogram = base_costs.get(name, 0)
            total_cost = base_cost_per_kilogram * weight
            
            #crea un nuevo objeto Product y lo agrega a la base de datos
            new_product = Product(name=name, weight=weight, quantity=quantity, base_cost_per_kilogram=base_cost_per_kilogram, total_cost=total_cost)
            db.session.add(new_product)
        
        db.session.commit()
        flash('Producto añadido al inventario', category='success')

    return render_template('add_stock.html')

#Interfaz para que el desarrollador pueda actualizar el stock de los productos
@views.route('/update_stock', methods=['GET', 'POST'])
def update_stock():
    #Si el usuario no está en sesión, se le redirige a la página de inicio de sesión
    if 'user_id' not in session:
        flash('Debe de iniciar sesión para acceder a esta página', category='error')
        return redirect(url_for('auth.login'))
    
    #Toma los datos del usuario en serion
    user = User.query.get(session['user_id'])

    #Si no es admin no se le permite acceso
    if not user or not user.is_admin:
        flash('No tiene permiso para acceder a esta página', category='error')
        return redirect(url_for('views.home'))
    
    #Si el metodo de solicitud es POST
    if request.method == 'POST':

        #Analiza todos los productos en la base de datos
        for product in Product.query.all():
       
            #fstring que indica que el argumento que llama varía con cada producto. Este argumento se mueve con cada valor obtenido dentro del POST form
            product_id = request.form.get(f'product_id_{product.id}')
            new_quantity = request.form.get(f'new_quantity_{product.id}')

            #Si el producto existe y la cantidad es válida, se actualiza la cantidad del producto
            if product_id and new_quantity:
                if int(new_quantity) < 0:
                    flash('No se puede ingresar una cantidad negativa', category='error')
                    return redirect(url_for('views.update_stock'))
                
                product.quantity = int(new_quantity)

        db.session.commit()
        flash('Stock actualizado', category='success')
        return redirect(url_for('views.update_stock'))
    
    #Si el método de solicitud es GET, se obtienen los productos dentro de la base de datos.   
    products = Product.query.order_by(Product.name, Product.weight).all()

    #Si no hay productos en la base de datos, se le notifica al usuario
    if not products:
        flash('No hay productos en el inventario', category='error')
        return redirect(url_for('views.admin_page'))
    
    #Renderiza la plantilla de actualización de stock
    return render_template('update_stock.html', products=products)    

@views.route('/delete_product', methods=['GET', 'POST'])
def delete_product():
    if 'user_id' not in session:
        flash('Debe de iniciar sesión para acceder a esta página', category='error')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])

    if not user or not user.is_admin:
        flash('No tiene permiso para acceder a esta página', category='error')
        return redirect(url_for('views.home'))
    
    if request.method == 'POST':

        #Obtiene el id del producto a eliminar
        product_id = request.form.get('product_id')
        product = Product.query.get(product_id)
        
        #Si el producto existe, se eliminan todos los items del carrito que contengan ese producto y se elimina el producto
        if product:
            carts = Cart.query.all()

            for cart in carts:
                for item in cart.cart_items:
                    if item.product.id == product.id:
                        db.session.delete(item)

            db.session.delete(product)
            db.session.commit()
            flash('Producto eliminado', category='success')
        else:
            return redirect(url_for('views.delete_product'))

    #Si el metodo es GET, se obtienen todos los productos ordenados por nombre y peso
    products = Product.query.order_by(Product.name, Product.weight).all()
    return render_template('delete_product.html', products=products)