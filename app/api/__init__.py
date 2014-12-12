import logging
from logging.handlers import RotatingFileHandler
import os
from flask.ext.oauthlib.client import OAuth

import sys
from flask import Flask, render_template, url_for, flash
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.form import ImageUploadField, thumbgen_filename
from flask.ext.admin.model.form import InlineFormAdmin
from flask.ext.admin import Admin, BaseView, expose, AdminIndexView

from flask.ext.autodoc import Autodoc
from flask.ext.login import LoginManager, current_user, logout_user, login_user
from flask.ext.sqlalchemy import SQLAlchemy

from itsdangerous import JSONWebSignatureSerializer as Serializer
from markupsafe import Markup
from sqlalchemy import String
from werkzeug.utils import secure_filename, redirect
from wtforms import SelectField, Form, ValidationError
from wtforms.validators import Optional
from app.api.users.constants import USER_ROLE_SELECT, USER_STATUS_SELECT, PROVIDER_LIST_SELECT
from app.decorators import admin_required
from config import SECRET_KEY, UPLOAD_FOLDER

# #######################
# Init                  #
# #######################
_basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder=UPLOAD_FOLDER)
app.config.from_object('config')
auto = Autodoc(app)
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.session_protection = None
oauth = OAuth(app)

twitter = oauth.remote_app(
    'twitter',
    consumer_key='AldBjkVl3fy2egNxP1ZYjC7YN',
    consumer_secret='cghj3MsOcHxDdyFGgjzxsMo96U9SmbFnCqu77s0nvA8ORSzmHa',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
)

facebook = oauth.remote_app(
    'facebook',
    consumer_key='488630447945634',
    consumer_secret='2bcd79a9f0f788aa70b832ea15e1e8fc',
    request_token_params={'scope': 'email'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth'
)

vkontakte = oauth.remote_app(
    'vkontakte',
    consumer_key='4675084',
    consumer_secret='pXdxGuIj1ki11TBBPZlc',
    base_url='https://api.vk.com/method/',
    request_token_url=None,
    access_token_url='https://oauth.vk.com/access_token',
    authorize_url='https://oauth.vk.com/authorize'
)

from app.api.forms import LoginForm


class MyAdminIndexView(AdminIndexView):

    @expose('/', methods=['POST', 'GET'])
    def index(self):
        # TODO: redirect to login page
        # if not current_user.is_authenticated():
        #     return render_template('forbidden_page.html')
        # if current_user.is_authenticated():
        #     return super(MyAdminIndexView, self).index()
        # form = LoginForm()
        # try:
        #     if form.validate_on_submit():
        #         login_user(User.query.filter_by(email=form.email.data).first(), remember=True)
        #         flash(u"Success login.", category='success')
        #         return super(MyAdminIndexView, self).index()
        # except ValidationError as v:
        #     flash(v.message, category='error')
        # return render_template("login.html", form=form)
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        # TODO: redirect to login page
        return redirect(url_for('.index'))


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


class RecipePhotoInlineModelForm(InlineFormAdmin):
    def postprocess_form(self, form):
        form.data = ImageUploadField('Image', base_path=app.config['RECIPES_UPLOAD'], thumbnail_size=(500, 500, True))
        return form


class ChefPhotoInlineModelForm(InlineFormAdmin):
    def postprocess_form(self, form):
        form.data = ImageUploadField('Image', base_path=app.config['CHEFS_UPLOAD'], thumbnail_size=(500, 500, True))
        return form


class SchoolPhotoInlineModelForm(InlineFormAdmin):
    def postprocess_form(self, form):
        form.data = ImageUploadField('Image', base_path=app.config['SCHOOLS_UPLOAD'], thumbnail_size=(500, 500, True))
        return form


class RecipeModelViewWithRelationships(ModelView):
    column_display_all_relations = True
    column_auto_select_related = True

    def _list_thumbnail_many(view, context, model, name):
        if not model.photos:
            return ''
        images_show = ''
        for photo in model.photos:
            images_show = images_show + Markup('<img src="%s">' % url_for('static', filename='recipes/' + thumbgen_filename(photo.data)))
        return images_show

    column_formatters = {
        "photos": _list_thumbnail_many
    }
    inline_models = (RecipePhotoInlineModelForm(RecipePhoto),)


class SchoolModelViewWithRelationships(ModelView):
    column_display_all_relations = True
    column_auto_select_related = True

    def _list_thumbnail_many(view, context, model, name):
        if not model.photos:
            return ''
        images_show = ''
        for photo in model.photos:
            images_show = images_show + Markup('<img src="%s">' % url_for('static', filename='schools/' + thumbgen_filename(photo.data)))
        return images_show

    column_formatters = {
        "photos": _list_thumbnail_many
    }
    inline_models = (SchoolPhotoInlineModelForm(SchoolPhoto),)


class RecipeImageForm(Form):
    data = ImageUploadField('Image', base_path=app.config['RECIPES_UPLOAD'], thumbnail_size=(500, 500, True))


class RecipeModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.data:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='recipes/' + thumbgen_filename(model.data)))

    def get_title(view, context, model, name):
        return model.data

    can_create = True
    column_list = ('data', 'title')
    column_formatters = {
        "data": _list_thumbnail,
        "title": get_title
    }
    form = RecipeImageForm


class ChefImageForm(Form):
    data = ImageUploadField('Image', base_path=app.config['CHEFS_UPLOAD'], thumbnail_size=(500, 500, True))


class ChefImageModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.data:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='chefs/' + thumbgen_filename(model.data)))

    def get_title(view, context, model, name):
        return model.data

    can_create = True
    column_list = ('data', 'title')
    column_formatters = {
        "data": _list_thumbnail,
        "title": get_title
    }
    form = ChefImageForm


class SchoolImageForm(Form):
    data = ImageUploadField('Image', base_path=app.config['SCHOOLS_UPLOAD'], thumbnail_size=(500, 500, True))


class SchoolModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.data:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='schools/' + thumbgen_filename(model.data)))

    def get_title(view, context, model, name):
        return model.data

    can_create = True
    column_list = ('data', 'title')
    column_formatters = {
        "data": _list_thumbnail,
        "title": get_title
    }
    form = SchoolImageForm


class ToolModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='tools/' + thumbgen_filename(model.photo)))

    can_create = True
    column_formatters = {
        "photo": _list_thumbnail,
    }

    form_extra_fields = {
        'photo': ImageUploadField('Image', base_path=app.config['TOOLS_UPLOAD'], thumbnail_size=(500, 500, True))
    }


class ChefModelViewWithUpload(ModelView):
    column_display_all_relations = True
    column_auto_select_related = True

    def _list_thumbnail_medium(view, context, model, name):
        if not model.medium_photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='chefs/' + thumbgen_filename(model.medium_photo)))

    def _list_thumbnail_main(view, context, model, name):
        if not model.main_photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='chefs/' + thumbgen_filename(model.main_photo)))

    def _list_thumbnail_many(view, context, model, name):
        if not model.photos:
            return ''
        images_show = ''
        for photo in model.photos:
            images_show = images_show + Markup('<img src="%s">' % url_for('static', filename='chefs/' + thumbgen_filename(photo.data)))
        return images_show

    can_create = True
    column_formatters = {
        "medium_photo": _list_thumbnail_medium,
        "main_photo": _list_thumbnail_main,
        "photos": _list_thumbnail_many

    }
    form_extra_fields = {
        'medium_photo': ImageUploadField('Medium photo', base_path=app.config['CHEFS_UPLOAD'], thumbnail_size=(500, 500, True)),
        'main_photo': ImageUploadField('Main photo', base_path=app.config['CHEFS_UPLOAD'], thumbnail_size=(500, 500, True))
    }
    inline_models = (ChefPhotoInlineModelForm(ChefPhoto),)


class SchoolItemModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='school_items/' + thumbgen_filename(model.photo)))

    can_create = True
    column_formatters = {
        "photo": _list_thumbnail,
    }

    form_extra_fields = {
        'photo': ImageUploadField('Image', base_path=app.config['SCHOOL_ITEMS_UPLOAD'], thumbnail_size=(500, 500, True))
    }


class InstructionItemModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='instruction_items/' + thumbgen_filename(model.photo)))

    can_create = True
    column_formatters = {
        "photo": _list_thumbnail,
    }

    form_extra_fields = {
        'photo': ImageUploadField('Image', base_path=app.config['INSTRUCTION_ITEMS_UPLOAD'], thumbnail_size=(500, 500, True))
    }


class MyUserAdmin(ModelView):
    column_exclude_list = ('_password',)
    form_edit_rules = ('role_code',)
    column_choices = {
        'role_code': USER_ROLE_SELECT,
        'provider_id': PROVIDER_LIST_SELECT,
        'status_code': USER_STATUS_SELECT
    }
    form_overrides = dict(role_code=SelectField, provider_id=SelectField, status_code=SelectField)

    def update_model(self, form, model):
        if self.form_edit_rules:
            for field in form:
                field_name = field.name
                if field_name not in self.form_edit_rules:
                    form.__delitem__(field_name)
        return super(MyUserAdmin, self).update_model(form, model)

    form_args = dict(
        role_code=dict(
            label='Role', choices=USER_ROLE_SELECT, coerce=int
        ),
        provider_id=dict(
            label='Provider', choices=PROVIDER_LIST_SELECT, coerce=int
        ),
        status_code=dict(
            label='Status', choices=USER_STATUS_SELECT, coerce=int
        ),
    )


admin.add_view(MyUserAdmin(User, db.session))
admin.add_view(ChefModelViewWithUpload(Chef, db.session))
admin.add_view(ModelView(Basket, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(CuisineType, db.session))
admin.add_view(ModelView(Dictionary, db.session))
admin.add_view(ModelView(Favorite, db.session))
admin.add_view(ModelView(Ingredient, db.session))
admin.add_view(ModelView(Like, db.session))
admin.add_view(RecipeModelViewWithUpload(RecipePhoto, db.session))
admin.add_view(ChefImageModelViewWithUpload(ChefPhoto, db.session))
admin.add_view(SchoolModelViewWithUpload(SchoolPhoto, db.session))
admin.add_view(InstructionItemModelViewWithUpload(InstructionItem, db.session))
admin.add_view(RecipeModelViewWithRelationships(Recipe, db.session))
admin.add_view(SchoolModelViewWithRelationships(School, db.session))
admin.add_view(SchoolItemModelViewWithUpload(SchoolItem, db.session))
admin.add_view(ToolModelViewWithUpload(Tool, db.session))
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
