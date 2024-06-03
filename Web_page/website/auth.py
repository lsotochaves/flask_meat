from flask import Blueprint, render_template, request, flash, redirect, url_for, session 
from .models import User, Product, Cart, CartItem
from werkzeug.security import generate_password_hash, check_password_hash #SEGURIDAD DE CONTRASEÑA (FUNCION DE UNA VÍA)
from . import db

auth = Blueprint('auth', __name__)

#Ruta para el proceso de login
@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':

        #Obtiene los credenciales que a los que se intentan acceder
        email = request.form.get('email')
        password = request.form.get('password1')

        #Consulta al usuario que coincida con el correo proporcionado      
        user = User.query.filter_by(email=email).first()

        #Verifica que el usuario exista y que la contraseña sea correctay
        if user:

            # Confirma que la contraseña sea correcta
            if check_password_hash(user.password, password):
                flash('Inicio de sesión exitoso!', category='success')
                 
                #Si el usuario es admin, redirige a la página de admin y además asigna las variables del usuario 
                if user.is_admin:
                    session['user_id'] = user.id
                    session['first_name'] = user.first_name
                    return redirect(url_for('views.admin_page'))
                
                #Crea el carrito para el usuario
                cart = Cart.query.filter_by(user_id=user.id).first()

                if cart is None:
                    cart = Cart(user_id=user.id)
                    db.session.add(cart)
                    db.session.commit()

                #Asigna las variables del usuario
                session['user_id'] = user.id
                session['first_name'] = user.first_name

                #Redirige a la página de inicio
                return redirect(url_for('views.home'))

            #Si la contraseña es incorrecta
            else:
                flash('Contraseña incorrecta, intente de nuevo', category= 'error')
        
        #Si el usuario no existe
        else:
            flash('El correo proporcionado no existe, intente de nuevo o cree una cuenta.', category='error')
        
    return render_template("login.html")

# Ruta para el proceso de registro
@auth.route("/sign-up", methods = ['GET', 'POST'])
def signup():

    #Toma los valores ingresados por el usuario
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get("last_name")
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        #Busca en la base de datos si el correo ya está en uso
        user = User.query.filter_by(email=email).first()

        #Si el correo está en uso, se le notifica al usuario
        if user:
            flash('El correo electrónico ya está en uso', category= 'error')

        #Si el correo no está en uso, pero es un correo inválido, se le notifica al usuario
        elif len(email) < 5: 
            flash('El correo debe de contener más de 4 caracteres', category = 'error')
        
        #Si el correo no está en uso, pero las contraseña no coinciden, se le notifica al usuario
        elif password1 != password2:
            flash('Las contraseñas son diferentes', category = 'error')
        elif len(password1) < 6:
            flash('La contraseña debe de tener al menos 6 caracteres', category = 'error')
        
        #Si nada de lo anterior ocurre, se crea el usuario
        else:
            # Se añade al usuario a la base de datos.
            new_user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1)) #Añade el usuario con una contraseña segura
            db.session.add(new_user) #Crea el usuario
            db.session.commit() #Actualiza a base de datos
            flash('Cuenta creada!', category = 'success')

            #Redirige al usuario a la página de inicio
            return redirect(url_for('views.home'))

    #Si el método es GET, se renderiza la página de registro            
    return render_template("signup.html")

@auth.route('/logout')
def logout():
    if 'user_id' not in session:
        return redirect(url_for('views.home'))

    user_id = session['user_id']
    cart = Cart.query.filter_by(user_id=user_id).first()
    if cart:

        #Obtiene los items dentro del carrito
        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()

        #Añade la cantidad al inventario de los items dentro del carrito.
        for item in cart_items:
            product = Product.query.get(item.product_id)
            if product:
                product.quantity += item.quantity
        
        #Elimina la reserva de tiempo del carrito
        cart.time_reserved = None

        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
    session['cart_count'] = 0

    #Elimina al variable de la sesion.
    session.pop('user_id', None)
    return redirect(url_for('views.home'))
