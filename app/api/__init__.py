import logging
from logging.handlers import RotatingFileHandler
import os

import sys
from flask import Flask, render_template
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.autodoc import Autodoc
from flask.ext.login import LoginManager, current_user, logout_user
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin, BaseView, expose, AdminIndexView

from itsdangerous import JSONWebSignatureSerializer as Serializer
from config import SECRET_KEY

# #######################
# Init                  #
# #######################
_basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.from_object('config')
auto = Autodoc(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)


class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        # TODO: redirect to login page
        # if not current_user.is_authenticated():
        #     return render_template('forbidden_page.html')
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        # TODO: redirect to login page
        # return redirect(url_for('.index'))


admin = Admin(app, index_view=MyAdminIndexView())

from app.api.chefs.model import Chef
from app.api.users.model import User
from app.api.basket.model import Basket
from app.api.categories.model import Category
from app.api.cuisine_types.model import CuisineType
from app.api.dictionary.model import Dictionary
from app.api.favorites.model import Favorite
from app.api.ingredients.model import Ingredient
from app.api.likes.model import Like
from app.api.photos.model import RecipePhoto, ChefPhoto, SchoolPhoto
from app.api.recipes.model import InstructionItem, Recipe
from app.api.schools.model import School, SchoolItem
from app.api.tools.model import Tool
from app.api.wines.model import Wine


class MyUserAdmin(ModelView):
    excluded_list_columns = ('_password',)


admin.add_view(MyUserAdmin(User, db.session))
admin.add_view(ModelView(Chef, db.session))
admin.add_view(ModelView(Basket, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(CuisineType, db.session))
admin.add_view(ModelView(Dictionary, db.session))
admin.add_view(ModelView(Ingredient, db.session))
admin.add_view(ModelView(Like, db.session))
admin.add_view(ModelView(RecipePhoto, db.session))
admin.add_view(ModelView(ChefPhoto, db.session))
admin.add_view(ModelView(SchoolPhoto, db.session))
admin.add_view(ModelView(InstructionItem, db.session))
admin.add_view(ModelView(Recipe, db.session))
admin.add_view(ModelView(School, db.session))
admin.add_view(ModelView(SchoolItem, db.session))
admin.add_view(ModelView(Tool, db.session))
admin.add_view(ModelView(Wine, db.session))

# #######################
# Configure Secret Key #
# #######################


def install_secret_key(app, filename='secret_key'):
    """Configure the SECRET_KEY from a file
    in the instance directory.

    If the file does not exist, print instructions
    to create it from a shell with a random key,
    then exit.
    """
    filename = os.path.join(app.instance_path, filename)

    try:
        app.config['SECRET_KEY'] = open(filename, 'rb').read()
    except IOError:
        print('Error: No secret key. Create it with:')
        full_path = os.path.dirname(filename)
        if not os.path.isdir(full_path):
            print('mkdir -p {filename}'.format(filename=full_path))
        print('head -c 24 /dev/urandom > {filename}'.format(filename=filename))
        sys.exit(1)


if not app.config['DEBUG']:
    install_secret_key(app)

# #######################
# Views                 #
# #######################

# Users module
from app.api.users.views import mod as users_module
app.register_blueprint(users_module)

# Categories module
from app.api.categories.views import mod as categories_module
app.register_blueprint(categories_module)

# Likes module
from app.api.likes.views import mod as likes_module
app.register_blueprint(likes_module)

# Favorites module
from app.api.favorites.views import mod as favorites_module
app.register_blueprint(favorites_module)

# Recipes module
from app.api.recipes.views import mod as recipes_module
app.register_blueprint(recipes_module)

# Chefs module
from app.api.chefs.views import mod as chefs_module
app.register_blueprint(chefs_module)

# Tools module
from app.api.tools.views import mod as tools_module
app.register_blueprint(tools_module)

# Dictionary module
from app.api.dictionary.views import mod as dictionary_module
app.register_blueprint(dictionary_module)

# Schools module
from app.api.schools.views import mod as schools_module
app.register_blueprint(schools_module)

# Cuisine types module
from app.api.cuisine_types.views import mod as cuisine_types_module
app.register_blueprint(cuisine_types_module)

# Ingredients types module
from app.api.ingredients.views import mod as ingredients_module
app.register_blueprint(ingredients_module)

# Wines types module
from app.api.wines.views import mod as wines_module
app.register_blueprint(wines_module)

# Baskets types module
from app.api.basket.views import mod as baskets_module
app.register_blueprint(baskets_module)

# docsmodule
from app.api.docs.views import mod as docs_module
app.register_blueprint(docs_module)

# #######################
# Logs Handler          #
# #######################


formatter = logging.Formatter("%(asctime)s\t%(name)s\t%(message)s")

error_handler = RotatingFileHandler(os.path.join(_basedir, '../../logs/error.log'), maxBytes=10000, backupCount=2)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)
app.logger.addHandler(error_handler)

info_handler = RotatingFileHandler(os.path.join(_basedir, '../../logs/info.log'), maxBytes=10000, backupCount=2)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)
app.logger.addHandler(info_handler)


# #######################
# Error Page handler    #
# #######################


@app.errorhandler(403)
def forbidden_page(error):
    return render_template("errors/forbidden_page.html"), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/page_not_found.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/server_error.html"), 500
