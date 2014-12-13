# coding=utf-8
from flask import request, jsonify, g, url_for, Blueprint, redirect, Flask
from flask.ext.login import login_required

from app.api import db, auto
from app.api.constants import OK, BAD_REQUEST
from app.api.helpers import *
from app.api.photos.model import *
from app.decorators import admin_required

mod = Blueprint('photos', __name__, url_prefix='/api/photos')


def new_photo(entity):
    title = request.json.get('title')
    item_id = request.json.get('item_id')
    if title is None or item_id is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    photo = entity(title=title, item_id=item_id)
    db.session.add(photo)
    db.session.commit()
    information = response_builder(photo, entity)
    return jsonify({'error_code': OK, 'result': information}), 201


def update_photo(id, entity):
    photo = entity.query.get(id)
    if not photo:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    if request.json.get('title'):
        photo.title = request.json.get('title')
    if request.json.get('item_id'):
        photo.item_id = request.json.get('item_id')
    db.session.commit()
    photo = entity.query.get(id)
    information = response_builder(photo, entity)
    return jsonify({'error_code': OK, 'result': information}), 200


def get_photo(id, entity):
    photo = entity.query.get(id)
    if not photo:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    information = response_builder(photo, entity)
    return jsonify({'error_code': OK, 'result': information}), 200


def get_all_photos(entity):
    photos = []
    for photo in entity.query.all():
        information = response_builder(photo, entity)
        photos.append(information)
    return jsonify({'error_code': OK, 'result': photos}), 200


def delete_photo(id, entity):
    photo = entity.query.get(id)
    if not photo:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    db.session.delete(photo)
    db.session.commit()
    return jsonify({'error_code': OK}), 200


def get_full_photos(id, entity):
    photos = []
    for photo in entity.query.filter_by(item_id=id):
        information = response_builder(photo, entity)
        photos.append(information)
    return jsonify({'error_code': OK, 'result': photos}), 200


# RecipePhoto

@auto.doc()
@mod.route('/recipe', methods=['POST'])
@login_required
@admin_required
def new_photo():
    """
    Add new photo for recipe. List of parameters in json request:
            title (required)
            item_id (required)
    Example of request:
            {"title":"good", "item_id":1}
    :return: json with parameters:
            error_code - server response_code
            result - information about created photo
    """
    new_photo(RecipePhoto)


@auto.doc()
@mod.route('/recipe/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_photo(id):
    """
    Update exists photo for recipe. List of parameters in json request:
            title (optional)
            item_id (optional)
    Example of request:
            {"title":"good", "item_id":1}
    :param id: photo id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated photo
    """
    update_photo(id, RecipePhoto)


@auto.doc()
@mod.route('/recipe/<int:id>', methods=['GET'])
@login_required
def get_photo(id):
    """
    Get information about photo for recipe.
    :param id: photo id
    :return: json with parameters:
            error_code - server response_code
            result - information about photo
    """
    get_photo(id, RecipePhoto)


@auto.doc()
@mod.route('/recipe/', methods=['GET'])
@login_required
def get_all_photos():
    """
    Get information about all exist photos for recipes.
    :return: json with parameters:
            error_code - server response_code
            result - information about photos
    """
    get_all_photos(RecipePhoto)


@auto.doc()
@mod.route('/recipe/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_photo(id):
    """
    Delete photo for recipe.
    :param id: photo id
    :return: json with parameters:
            error_code - server response_code
    """
    delete_photo(id, RecipePhoto)


@auto.doc()
@mod.route('/fullrecipe/<int:id>', methods=['GET'])
@login_required
def get_recipe_photos(id):
    """
    Get information about all photos for recipe with special id.
    :param id: recipe id
    :return: json with parameters:
            error_code - server response_code
            result - information about photos
    """
    get_full_photos(id, RecipePhoto)

# ChefPhoto

@auto.doc()
@mod.route('/chef', methods=['POST'])
@login_required
@admin_required
def new_photo():
    """
    Add new photo for chef. List of parameters in json request:
            title (required)
            item_id (required)
    Example of request:
            {"title":"good", "item_id":1}
    :return: json with parameters:
            error_code - server response_code
            result - information about created photo
    """
    new_photo(ChefPhoto)


@auto.doc()
@mod.route('/chef/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_photo(id):
    """
    Update exists photo for chef. List of parameters in json request:
            title (optional)
            item_id (optional)
    Example of request:
            {"title":"good", "item_id":1}
    :param id: photo id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated photo
    """
    update_photo(id, ChefPhoto)


@auto.doc()
@mod.route('/chef/<int:id>', methods=['GET'])
@login_required
def get_photo(id):
    """
    Get information about photo for chef.
    :param id: photo id
    :return: json with parameters:
            error_code - server response_code
            result - information about photo
    """
    get_photo(id, ChefPhoto)


@auto.doc()
@mod.route('/chef/', methods=['GET'])
@login_required
def get_all_photos():
    """
    Get information about all exist photos for chefs.
    :return: json with parameters:
            error_code - server response_code
            result - information about photos
    """
    get_all_photos(ChefPhoto)


@auto.doc()
@mod.route('/chef/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_photo(id):
    """
    Delete photo for chefs.
    :param id: photo id
    :return: json with parameters:
            error_code - server response_code
    """
    delete_photo(id, ChefPhoto)


@auto.doc()
@mod.route('/fullchef/<int:id>', methods=['GET'])
@login_required
def get_chef_photos(id):
    """
    Get information about all photos for chef with special id.
    :param id: chef id
    :return: json with parameters:
            error_code - server response_code
            result - information about photos
    """
    get_full_photos(id, ChefPhoto)

# SchoolPhoto

@auto.doc()
@mod.route('/school', methods=['POST'])
@login_required
@admin_required
def new_photo():
    """
    Add new photo for school. List of parameters in json request:
            title (required)
            item_id (required)
    Example of request:
            {"title":"good", "item_id":1}
    :return: json with parameters:
            error_code - server response_code
            result - information about created photo
    """
    new_photo(SchoolPhoto)

@auto.doc()
@mod.route('/school/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_photo(id):
    """
    Update exists photo for school. List of parameters in json request:
            title (optional)
            item_id (optional)
    Example of request:
            {"title":"good", "item_id":1}
    :param id: photo id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated photo
    """
    update_photo(id, SchoolPhoto)


@auto.doc()
@mod.route('/school/<int:id>', methods=['GET'])
@login_required
def get_photo(id):
    """
    Get information about photo for school.
    :param id: photo id
    :return: json with parameters:
            error_code - server response_code
            result - information about photo
    """
    get_photo(id, SchoolPhoto)


@auto.doc()
@mod.route('/school/', methods=['GET'])
@login_required
def get_all_photos():
    """
    Get information about all exist photos for schools.
    :return: json with parameters:
            error_code - server response_code
            result - information about photos
    """
    get_all_photos(SchoolPhoto)


@auto.doc()
@mod.route('/school/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_photo(id):
    """
    Delete photo for school.
    :param id: photo id
    :return: json with parameters:
            error_code - server response_code
    """
    delete_photo(id, SchoolPhoto)


@auto.doc()
@mod.route('/fullschool/<int:id>', methods=['GET'])
@login_required
def get_school_photos(id):
    """
    Get information about all photos for school with special id.
    :param id: school id
    :return: json with parameters:
            error_code - server response_code
            result - information about photos
    """
    get_full_photos(id, SchoolPhoto)