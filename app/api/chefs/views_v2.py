from flask import request, jsonify, g, url_for, Blueprint, redirect, Flask
from flask.ext.login import login_required
from app.api import auto
from app.api.categories.model import Category
from app.api.constants import OK, BAD_REQUEST

from app.api.helpers import *
from app.api.chefs.model import *
from app.api.photos.model import RecipePhoto
from app.api.recipes.views_v2 import recipe_response_builder
from app.decorators import admin_required

mod = Blueprint('chefs_v2', __name__, url_prefix='/api_v2/chefs')


@auto.doc()
@mod.route('/', methods=['POST'])
@login_required
@admin_required
def new_chef():
    """
    Add new chef. List of parameters in json request:
            email (required)
            last_name (required)
            first_name (optional)
            work (optional)
            biography (optional)
            quote (optional)
            main_photo (optional)
            medium_photo (optional)
    Example of request:
            {"first_name":"alex", "last_name":"smith", "email":"smth@mail.ru", "main_photo":"", "medium_photo":""}
    :return: json with parameters:
            error_code - server response_code
            result - information about created chef
    """
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    work = request.json.get('work')
    biography = request.json.get('biography')
    quote = request.json.get('quote')
    email = request.json.get('email')
    main_photo = request.json.get('main_photo')
    medium_photo = request.json.get('medium_photo')
    if last_name is None or email is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    chef = Chef(first_name=first_name, last_name=last_name, work=work, biography=biography, quote=quote, email=email,
                main_photo=main_photo, medium_photo=medium_photo)
    db.session.add(chef)
    db.session.commit()
    information = response_builder(chef, Chef)
    return jsonify({'error_code': OK, 'result': information}), 201


@auto.doc()
@mod.route('/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_chef(id):
    """
    Update exists chef. List of parameters in json request:
            email (optional)
            last_name (optional)
            first_name (optional)
            work (optional)
            biography (optional)
            quote (optional)
            main_photo (optional)
            medium_photo (optional)
    Example of request:
            {"first_name":"alex", "last_name":"smith", "email":"smth@mail.ru", "main_photo":"", "medium_photo":""}
    :param id: chef id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated chef
    """
    chef = Chef.query.get(id)
    if not chef:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    if request.json.get('first_name'):
        chef.first_name = request.json.get('first_name')
    if request.json.get('last_name'):
        chef.last_name = request.json.get('last_name')
    if request.json.get('work'):
        chef.work = request.json.get('work')
    if request.json.get('biography'):
        chef.biography = request.json.get('biography')
    if request.json.get('quote'):
        chef.quote = request.json.get('quote')
    if request.json.get('email'):
        chef.email = request.json.get('email')
    if request.json.get('main_photo'):
        chef.main_photo = request.json.get('main_photo')
    if request.json.get('medium_photo'):
        chef.medium_photo = request.json.get('medium_photo')
    db.session.commit()
    chef = chef.query.get(id)
    information = response_builder(chef, Chef)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
def get_chef(id):
    """
    Get information about chef (with list of his recipes and photos, without main photo and work).
    :param id: chef id
    :return: json with parameters:
            error_code - server response_code
            result - information about chef
    """
    chef = Chef.query.get(id)
    lang = request.args.get('lang', type=unicode, default=u'en')
    if not chef:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # chef with `id` isn't exist
    information = chef_response_builder(chef, lang)
    hash_of_information = make_hash(information)
    information['hash'] = hash_of_information
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
def get_all_chefs():
    """
    Get short information about all exist chefs - email, last_name, first_name, work, main_photo
    :param offset (GET param) : starts from which chef
    :param limit (GET param) : how many chefs you want to get
    :return: json with parameters:
            error_code - server response_code
            result - information about chefs
            entities_count - numbers of all chefs
    """
    chefs = []
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', type=int)
    lang = request.args.get('lang', type=unicode, default=u'en')
    count = Chef.query.count()
    if limit is not None and offset is not None:
        chefs_band = Chef.query.slice(start=offset, stop=limit+offset).all()
    else:
        chefs_band = Chef.query.all()
    for chef in chefs_band:
        information = response_builder(chef, Chef, lang)
        information['photos'] = []
        for photo in ChefPhoto.query.filter_by(item_id=chef.id):
            photo_information = response_builder(photo, ChefPhoto, lang)
            information['photos'].append(photo_information)
        hash_of_information = make_hash(information)
        information['hash'] = hash_of_information
        chefs.append(information)
    ids = []
    chefs_ids = Chef.query.all()
    for chef_id in chefs_ids:
        ids.append(chef_id.id)
    return jsonify({'error_code': OK, 'result': chefs, 'entities_count': count, 'ids': ids}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_chef(id):
    """
    Delete chef.
    :param id: chef id
    :return: json with parameters:
            error_code - server response_code
    """
    chef = Chef.query.get(id)
    if not chef:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # chef with `id` isn't exist
    db.session.delete(chef)
    db.session.commit()
    return jsonify({'error_code': OK}), 200


def chef_response_builder(chef, lang=u'en'):
    information = response_builder(chef, Chef, lang)
    information['photos'] = []
    for photo in ChefPhoto.query.filter_by(item_id=chef.id):
        photo_information = response_builder(photo, ChefPhoto, lang)
        information['photos'].append(photo_information)
    # information['recipes'] = []
    # if current_user.is_authenticated() and current_user.role_code == 0:
    #     recipe_query = Recipe.query
    # else:
    #     recipe_query = Recipe.query.filter_by(type=PUBLISHED)
    # for recipe in recipe_query.filter_by(chef_id=chef.id):
    #     recipe_information = recipe_response_builder(recipe, lang, excluded=['chef_id'])
    #     information['recipes'].append(recipe_information)
    return information
    # information['recipes'] = []
    # for recipe in Recipe.query.filter_by(chef_id=id):
    #     recipe_information = response_builder(recipe, Recipe, excluded=['description', 'spicy', 'complexity', 'time',
    #                                                                     'amount_of_persons', 'chef_id', 'video'])
    #     categories = []
    #     for category in Recipe.query.filter_by(id=recipe.id).first().categories:
    #         categories.append(category.id)
    #     recipe_information['categories'] = []
    #     if categories is not None:
    #         for category_id in categories:
    #             category = Category.query.get(category_id)
    #             category_information = response_builder(category, Category)
    #             recipe_information["categories"].append(category_information)
    #     recipe_information['photos'] = []
    #     for photo in RecipePhoto.query.filter_by(item_id=recipe.id):
    #         photo_information = response_builder(photo, RecipePhoto)
    #         recipe_information['photos'].append(photo_information)
    #     information['recipes'].append(recipe_information)