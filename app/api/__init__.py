import logging
from logging.handlers import RotatingFileHandler
import os
from flask.ext.oauthlib.client import OAuth

import sys
from flask import Flask, render_template, url_for, flash, session
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.form import ImageUploadField, thumbgen_filename, ImageUploadInput
from flask.ext.admin.model.form import InlineFormAdmin
from flask.ext.admin import Admin, BaseView, expose, AdminIndexView

from flask.ext.autodoc import Autodoc
from flask.ext.login import LoginManager, current_user, logout_user, login_user
from flask.ext.sqlalchemy import SQLAlchemy

from markupsafe import Markup
from werkzeug.utils import secure_filename, redirect
from wtforms import SelectField, Form, ValidationError, TextField, IntegerField
from app.api.users.constants import USER_ROLE_SELECT, USER_STATUS_SELECT, PROVIDER_LIST_SELECT, RECIPE_TYPE_SELECT
from config import SECRET_KEY, UPLOAD_FOLDER

from flask import Flask
from flask_mail import Mail
# #######################
# Init                  #
# #######################
_basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder=UPLOAD_FOLDER)
app.config.from_object('config')
auto = Autodoc(app)
db = SQLAlchemy(app)
mail = Mail(app)

app.debug = True
# toolbar = DebugToolbarExtension(app)

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

# facebook = oauth.remote_app(
#     'facebook',
#     consumer_key='488630447945634',
#     consumer_secret='2bcd79a9f0f788aa70b832ea15e1e8fc',
#     request_token_params={'scope': 'email'},
#     base_url='https://graph.facebook.com',
#     request_token_url=None,
#     access_token_url='/oauth/access_token',
#     authorize_url='https://www.facebook.com/dialog/oauth'
# )

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


class ModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated()


class MyAdminIndexView(AdminIndexView):
    @expose('/', methods=['POST', 'GET'])
    def index(self):
        if current_user.is_authenticated() and current_user.is_admin():
            return super(MyAdminIndexView, self).index()
        form = LoginForm()
        try:
            if form.validate_on_submit():
                login_user(User.query.filter_by(email=form.email.data).first(), remember=True)
                session['email'] = form.email.data
                if not current_user.is_admin():
                    return render_template('errors/forbidden_page.html')
                flash(u"Success login as admin.", category='success')
                return super(MyAdminIndexView, self).index()
        except ValidationError as v:
            pass
        #     flash(v.message, category='error')
        return render_template("login.html", form=form)


class LogoutView(BaseView):
    @expose('/')
    def logout_view(self):
        logout_user()
        return redirect('/admin/')


admin = Admin(app, index_view=MyAdminIndexView())

from app.api.chefs.model import Chef
from app.api.users.model import User, Report
from app.api.basket.model import Basket
from app.api.categories.model import Category
from app.api.cuisine_types.model import CuisineType
from app.api.dictionary.model import Dictionary
from app.api.favorites.model import Favorite, FavoriteWine
from app.api.ingredients.model import Ingredient
from app.api.likes.model import Like, LikeWine
from app.api.photos.model import RecipePhoto, ChefPhoto, SchoolPhoto
from app.api.recipes.model import InstructionItem, Recipe
from app.api.schools.model import School, SchoolItem
from app.api.tools.model import Tool
from app.api.wines.model import Wine
from app.api.school_events.model import SchoolEvent
from app.api.sets.model import Set
from app.api.type_of_grape.model import TypeOfGrape
from app.api.promo_codes.model import PromoCode
from app.api.helpers import code_generator


class MyImageUploadInput(ImageUploadInput):
        data_template = ('<div class="image-thumbnail">'
                         ' <img %(image)s>'
                         '</div>'
                         '<input %(file)s>')


class MyImageUploadField(ImageUploadField):
    widget = MyImageUploadInput()


class RecipePhotoInlineModelForm(InlineFormAdmin):
    form_excluded_columns = ('photo', 'creation_date')

    def postprocess_form(self, form):
        form.photo = MyImageUploadField('Image', base_path=app.config['RECIPES_UPLOAD'],
                                        url_relative_path='recipes/')
        return form


class ChefPhotoInlineModelForm(InlineFormAdmin):
    form_excluded_columns = ('photo', 'creation_date')

    def postprocess_form(self, form):
        form.photo = MyImageUploadField('Image', base_path=app.config['CHEFS_UPLOAD'],
                                        url_relative_path='chefs/')
        return form


class SchoolPhotoInlineModelForm(InlineFormAdmin):
    form_excluded_columns = ('photo', 'creation_date')

    def postprocess_form(self, form):
        form.photo = MyImageUploadField('Image', base_path=app.config['SCHOOLS_UPLOAD'],
                                        url_relative_path='schools/')
        return form


class InstructionItemInlineModelForm(InlineFormAdmin):

    def postprocess_form(self, form):
        form.photo = MyImageUploadField('Image', base_path=app.config['SCHOOLS_UPLOAD'],
                                        url_relative_path='schools/')
        return form


class RecipeModelViewWithRelationships(ModelView):
    inline_models = (RecipePhotoInlineModelForm(RecipePhoto), Ingredient, InstructionItemInlineModelForm(InstructionItem))
    column_display_all_relations = True
    column_auto_select_related = True
    can_create = True
    can_edit = True
    column_choices = {
        'type': RECIPE_TYPE_SELECT
    }
    form_overrides = dict(type=SelectField)

    form_args = dict(
        type=dict(
            label='Type', choices=RECIPE_TYPE_SELECT, coerce=int
        ),
    )

    def time_sec_to_min(view, context, model, name):
        time_sec = int(model.time) % 60
        time_min = int(model.time) / 60 % 60
        if time_sec < 10:
            time_sec = "0" + str(time_sec)
        if time_min < 10:
            time_min = "0" + str(time_min)
        time_hour = int(model.time) / 3600
        time = str(time_hour) + ":" + str(time_min) + ":" + str(time_sec)
        return time

    def _list_thumbnail_many(view, context, model, name):
        if not model.photos:
            return ''
        images_show = ''
        for photo in model.photos:
            if photo.photo is None:
                return ''
            images_show = images_show + Markup('<img src="%s">' % url_for('static', filename='recipes/' + photo.photo))
        return images_show

    column_formatters = {
        "photos": _list_thumbnail_many,
        "time": time_sec_to_min,
    }

    form_extra_fields = {
        'time': TextField('Time (format: XX:XX:XX (hour:min:sec) )')
    }

    def on_model_change(self, form, model, is_created):
        time = str(model.time).split(':')
        try:
            new_time = int(time[0]) * 3600 + int(time[1]) * 60 + int(time[2])
        except Exception:
            new_time = 0
        model.time = new_time
        return


class SchoolModelViewWithRelationships(ModelView):
    column_display_all_relations = True
    column_auto_select_related = True

    def _list_thumbnail_many(view, context, model, name):
        if not model.photos:
            return ''
        images_show = ''
        for photo in model.photos:
            if photo.photo is None:
                return ''
            images_show = images_show + Markup('<img src="%s">' % url_for('static', filename='schools/' + photo.photo))
        return images_show

    column_formatters = {
        "photos": _list_thumbnail_many
    }
    inline_models = (SchoolPhotoInlineModelForm(SchoolPhoto),)


class RecipeImageForm(Form):
    photo = ImageUploadField('Image', base_path=app.config['RECIPES_UPLOAD'],
                             url_relative_path='recipes/')


class RecipeModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='recipes/' + model.photo))

    def get_title(view, context, model, name):
        return model.photo

    can_create = True
    column_list = ('photo', 'title')
    column_formatters = {
        "photo": _list_thumbnail,
        "title": get_title
    }
    form = RecipeImageForm


class ChefImageForm(Form):
    photo = ImageUploadField('Image', base_path=app.config['CHEFS_UPLOAD'],
                             url_relative_path='chefs/')


class ChefImageModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='chefs/' + model.photo))

    def get_title(view, context, model, name):
        return model.photo

    can_create = True
    column_list = ('photo', 'title')
    column_formatters = {
        "photo": _list_thumbnail,
        "title": get_title
    }
    form = ChefImageForm


class SchoolImageForm(Form):
    photo = ImageUploadField('Image', base_path=app.config['SCHOOLS_UPLOAD'],
                             url_relative_path='schools/')


class SchoolModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='schools/' + model.photo))

    def get_title(view, context, model, name):
        return model.photo

    can_create = True
    column_list = ('photo', 'title')
    column_formatters = {
        "photo": _list_thumbnail,
        "title": get_title
    }
    form = SchoolImageForm


class ToolModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='tools/' + model.photo))

    can_create = True
    column_formatters = {
        "photo": _list_thumbnail,
    }

    form_extra_fields = {
        'photo': ImageUploadField('Image', base_path=app.config['TOOLS_UPLOAD'],
                                  url_relative_path='tools/')
    }


class ChefModelViewWithUpload(ModelView):
    column_display_all_relations = True
    column_auto_select_related = True

    def _list_thumbnail_medium(view, context, model, name):
        if not model.medium_photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='chefs/' + model.medium_photo))

    def _list_thumbnail_main(view, context, model, name):
        if not model.main_photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='chefs/' + model.main_photo))

    def _list_thumbnail_many(view, context, model, name):
        if not model.photos:
            return ''
        images_show = ''
        for photo in model.photos:
            if photo.photo is None:
                return ''
            images_show = images_show + Markup('<img src="%s">' % url_for('static', filename='chefs/' + photo.photo))
        return images_show

    can_create = True
    column_formatters = {
        "medium_photo": _list_thumbnail_medium,
        "main_photo": _list_thumbnail_main,
        "photos": _list_thumbnail_many

    }
    form_extra_fields = {
        'medium_photo': ImageUploadField('Medium photo', base_path=app.config['CHEFS_UPLOAD'],
                                         url_relative_path='chefs/'),
        'main_photo': ImageUploadField('Main photo', base_path=app.config['CHEFS_UPLOAD'],
                                       url_relative_path='chefs/')
    }
    inline_models = (ChefPhotoInlineModelForm(ChefPhoto),)


class SchoolItemModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='school_items/' + model.photo))

    can_create = True
    column_formatters = {
        "photo": _list_thumbnail,
    }

    form_extra_fields = {
        'photo': ImageUploadField('Image', base_path=app.config['SCHOOL_ITEMS_UPLOAD'],
                                  url_relative_path='school_items/')
    }


class CategoryModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='categories/' + model.photo))

    can_create = True
    column_formatters = {
        "photo": _list_thumbnail,
    }

    form_extra_fields = {
        'photo': ImageUploadField('Image', base_path=app.config['CATEGORY_UPLOAD'],
                                  url_relative_path='categories/')
    }


class TypeOfGrapeModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='type_of_grapes/' + model.photo))

    can_create = True
    column_formatters = {
        "photo": _list_thumbnail,
    }

    form_extra_fields = {
        'photo': ImageUploadField('Image', base_path=app.config['TYPE_OF_GRAPE_UPLOAD'],
                                  url_relative_path='type_of_grapes/')
    }


class WineModelViewWithUpload(ModelView):
    def _list_thumbnail_photo(view, context, model, name):
        if not model.photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='wines/' + model.photo))

    def _list_thumbnail_flag_photo(view, context, model, name):
        if not model.flag_photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='wines/' + model.flag_photo))

    can_create = True
    column_formatters = {
        "photo": _list_thumbnail_photo,
        "flag_photo": _list_thumbnail_flag_photo,
    }

    form_extra_fields = {
        'photo': ImageUploadField('Image', base_path=app.config['WINE_UPLOAD'],
                                  url_relative_path='wines/'),
        'flag_photo': ImageUploadField('Flag image', base_path=app.config['WINE_UPLOAD'],
                                       url_relative_path='wines/')
    }


class SetModelViewWithUpload(ModelView):
    column_display_all_relations = True
    column_auto_select_related = True
    form_excluded_columns = ('user_sets',)
    column_exclude_list = ('user_sets',)

    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='sets/' + model.photo))

    can_create = True
    column_formatters = {
        "photo": _list_thumbnail,
    }

    form_extra_fields = {
        'photo': ImageUploadField('Image', base_path=app.config['SET_UPLOAD'],
                                  url_relative_path='sets/')
    }


class InstructionItemModelViewWithUpload(ModelView):

    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''
        return Markup('<img src="%s">' % url_for('static', filename='instruction_items/' + model.photo))

    def time_sec_to_min(view, context, model, name):
        if not model.time:
            model.time = 0
        time_sec = int(model.time) % 60
        time_min = int(model.time) / 60 % 60
        if time_sec < 10:
            time_sec = "0" + str(time_sec)
        if time_min < 10:
            time_min = "0" + str(time_min)
        time_hour = int(model.time) / 3600
        time = str(time_hour) + ":" + str(time_min) + ":" + str(time_sec)
        return time

    can_create = True
    column_formatters = {
        "photo": _list_thumbnail,
        "time": time_sec_to_min,
    }

    form_extra_fields = {
        'photo': ImageUploadField('Image', base_path=app.config['INSTRUCTION_ITEMS_UPLOAD'],
                                  url_relative_path='instruction_items/'),
        'time': TextField('Time (format: XX:XX:XX (hour:min:sec) ))')
    }

    def on_model_change(self, form, model, is_created):
        time = model.time.split(':')
        try:
            new_time = int(time[0]) * 3600 + int(time[1]) * 60 + int(time[2])
        except Exception:
            new_time = 0
        model.time = new_time
        return


class PromoCodeModel(ModelView):
    column_exclude_list = ('creation_date',)
    column_list = ('number', 'value', 'code')

    def get_number(view, context, model, name):
        return "%04d" % model.id

    can_create = True
    can_edit = False

    column_formatters = {
        "number": get_number,
    }

    form_extra_fields = {
        'amount': IntegerField('Amount')
    }
    form_columns = ('amount', 'value')

    def on_model_change(self, form, model, is_created):
        for i in range(model.amount - 1):
            value = "%04d" % int(model.value)
            code = code_generator()
            promo_code = PromoCode(value=value, code=code)
            db.session.add(promo_code)
            db.session.commit()
        model.value = "%04d" % int(model.value)
        model.code = code_generator()
        return


class SchoolEventModelView(ModelView):
    column_display_all_relations = True


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
admin.add_view(CategoryModelViewWithUpload(Category, db.session))
admin.add_view(TypeOfGrapeModelViewWithUpload(TypeOfGrape, db.session))
admin.add_view(ModelView(CuisineType, db.session))
admin.add_view(ModelView(Dictionary, db.session))
admin.add_view(ModelView(Favorite, db.session))
# admin.add_view(ModelView(Ingredient, db.session))
admin.add_view(ModelView(Like, db.session))
admin.add_view(ModelView(LikeWine, db.session))
# admin.add_view(RecipeModelViewWithUpload(RecipePhoto, db.session))
# admin.add_view(ChefImageModelViewWithUpload(ChefPhoto, db.session))
# admin.add_view(SchoolModelViewWithUpload(SchoolPhoto, db.session))
# admin.add_view(InstructionItemModelViewWithUpload(InstructionItem, db.session))
admin.add_view(RecipeModelViewWithRelationships(Recipe, db.session))
admin.add_view(SchoolModelViewWithRelationships(School, db.session))
admin.add_view(SchoolItemModelViewWithUpload(SchoolItem, db.session))
admin.add_view(ToolModelViewWithUpload(Tool, db.session))
admin.add_view(WineModelViewWithUpload(Wine, db.session))
admin.add_view(SchoolEventModelView(SchoolEvent, db.session))
admin.add_view(ModelView(Report, db.session))
admin.add_view(ModelView(FavoriteWine, db.session))
admin.add_view(SetModelViewWithUpload(Set, db.session))
admin.add_view(PromoCodeModel(PromoCode, db.session))
admin.add_view(LogoutView(name='Logout'))

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

# Users module (v2)
from app.api.users.views_v2 import mod as users_v2_module
app.register_blueprint(users_v2_module)

# Categories module
from app.api.categories.views import mod as categories_module
app.register_blueprint(categories_module)

# Categories module (v2)
from app.api.categories.views_v2 import mod as categories_v2_module
app.register_blueprint(categories_v2_module)

# Sets module
from app.api.sets.views_v2 import mod as sets_module
app.register_blueprint(sets_module)

# Likes module
from app.api.likes.views import mod as likes_module
app.register_blueprint(likes_module)

# Likes module (v2)
from app.api.likes.views_v2 import mod as likes_v2_module
app.register_blueprint(likes_v2_module)

# Favorites module
from app.api.favorites.views import mod as favorites_module
app.register_blueprint(favorites_module)

# Favorites module (v2)
from app.api.favorites.views_v2 import mod as favorites_v2_module
app.register_blueprint(favorites_v2_module)

# Recipes module
from app.api.recipes.views import mod as recipes_module
app.register_blueprint(recipes_module)

# Recipes module (v2)
from app.api.recipes.views_v2 import mod as recipes_v2_module
app.register_blueprint(recipes_v2_module)

# Chefs module
from app.api.chefs.views import mod as chefs_module
app.register_blueprint(chefs_module)

# Chefs module (v2)
from app.api.chefs.views_v2 import mod as chefs_v2_module
app.register_blueprint(chefs_v2_module)

# Tools module
from app.api.tools.views import mod as tools_module
app.register_blueprint(tools_module)

# Tools module (v2)
from app.api.tools.views_v2 import mod as tools_v2_module
app.register_blueprint(tools_v2_module)

# Dictionary module
from app.api.dictionary.views import mod as dictionary_module
app.register_blueprint(dictionary_module)

# Dictionary module
from app.api.dictionary.views_v2 import mod as dictionary_v2_module
app.register_blueprint(dictionary_v2_module)

# Schools module
from app.api.schools.views import mod as schools_module
app.register_blueprint(schools_module)

# Schools module (v2)
from app.api.schools.views_v2 import mod as schools_v2_module
app.register_blueprint(schools_v2_module)

# Cuisine types module
from app.api.cuisine_types.views import mod as cuisine_types_module
app.register_blueprint(cuisine_types_module)

# Cuisine types module (v2)
from app.api.cuisine_types.views_v2 import mod as cuisine_types_v2_module
app.register_blueprint(cuisine_types_v2_module)

# Ingredients types module
from app.api.ingredients.views import mod as ingredients_module
app.register_blueprint(ingredients_module)

# Ingredients types module (v2)
from app.api.ingredients.views_v2 import mod as ingredients_v2_module
app.register_blueprint(ingredients_v2_module)

# Wines types module
from app.api.wines.views import mod as wines_module
app.register_blueprint(wines_module)

# Wines types module (v2)
from app.api.wines.views_v2 import mod as wines_v2_module
app.register_blueprint(wines_v2_module)

# Baskets types module
from app.api.basket.views import mod as baskets_module
app.register_blueprint(baskets_module)

# Baskets types module (v2)
from app.api.basket.views_v2 import mod as baskets_v2_module
app.register_blueprint(baskets_v2_module)

# School events module
from app.api.school_events.views import mod as school_events_module
app.register_blueprint(school_events_module)

# School events module (v2)
from app.api.school_events.views_v2 import mod as school_events_v2_module
app.register_blueprint(school_events_v2_module)

# Types of grape module (v2)
from app.api.type_of_grape.views_v2 import mod as type_of_grape_v2_module
app.register_blueprint(type_of_grape_v2_module)

# Promo codes module (v2)
from app.api.promo_codes.views_v2 import mod as promo_codes_v2_module
app.register_blueprint(promo_codes_v2_module)

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
