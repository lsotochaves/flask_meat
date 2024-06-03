from os import path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = "database.db"
def create_app():
    #Crea una instancia de Flask y la asocia a la variable app
    app = Flask(__name__)

    #Crea una llave secreta para le sesión del usuario. Esto permite que la aplicación sepa que está hablando con el usuario verdadero en la sesión.
    app.secret_key = "snbiosdmboimsbmiobramkflamgkemglkemgmewslgmanwgionvklmgkldm"

    #Determina la localización de la base de datos.
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' 

    db.init_app(app) #inicializa la base de datos
    #Obtiene las rutas que se utilizan en el programa.
    from .views import views
    from .auth import auth
    from .cart import cart
    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')
    app.register_blueprint(cart, url_prefix = '/')

    #Crea la base de datos con los modelos definidos en models.py
    from .models import User, Product, Cart, CartItem
    create_database(app)

    return app

#Función encargada de crear la base de datos.
def create_database(app):
    #Si la base de datos no existe, la crea
    if not path.exists('website/' + DB_NAME):
            with app.app_context():  # Crea un application-context
                db.create_all()
            print('Base de datos creada.')