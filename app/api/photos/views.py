# coding=utf-8
from flask import request, jsonify, g, url_for, Blueprint, redirect, Flask

from app.api import db, auth
from app.api.helpers import *
from app.api.photos.model import *

mod = Blueprint('photos', __name__, url_prefix='/api/photos')


def new_photo(entity):
    title = request.json.get('title')
    item_id = request.json.get('item_id')
    if title is None or item_id is None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    photo = entity(title=title, item_id=item_id)
    db.session.add(photo)
    db.session.commit()
    information = response_builder(photo, entity)
    return jsonify({'error_code': 201, 'result': information}), 201


def update_photo(id, entity):
    photo = entity.query.get(id)
    if not photo:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    if request.json.get('title'):
        photo.title = request.json.get('title')
    if request.json.get('item_id'):
        photo.item_id = request.json.get('item_id')
    db.session.commit()
    photo = entity.query.get(id)
    information = response_builder(photo, entity)
    return jsonify({'error_code': 200, 'result': information}), 200


def get_photo(id, entity):
    photo = entity.query.get(id)
    if not photo:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    information = response_builder(photo, entity)
    return jsonify({'error_code': 200, 'result': information}), 200


def get_all_photos(entity):
    photos = []
    for photo in entity.query.all():
        information = response_builder(photo, entity)
        photos.append(information)
    return jsonify({'error_code': 200, 'result': photos}), 200


def delete_photo(id, entity):
    photo = entity.query.get(id)
    if not photo:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    db.session.delete(photo)
    db.session.commit()
    return jsonify({'error_code': 200}), 200

# RecipePhoto

@mod.route('/recipe', methods=['POST'])
def new_photo():
    new_photo(RecipePhoto)


@mod.route('/recipe/<int:id>', methods=['PUT'])
def update_photo(id):
    update_photo(id, RecipePhoto)


@mod.route('/recipe/<int:id>', methods=['GET'])
def get_photo(id):
    get_photo(id, RecipePhoto)


@mod.route('/recipe/', methods=['GET'])
def get_all_photos():
    get_all_photos(RecipePhoto)


@mod.route('/recipe/<int:id>', methods=['DELETE'])
def delete_photo(id):
    delete_photo(id, RecipePhoto)

# ChefPhoto

@mod.route('/chef', methods=['POST'])
def new_photo():
    new_photo(ChefPhoto)


@mod.route('/chef/<int:id>', methods=['PUT'])
def update_photo(id):
    update_photo(id, ChefPhoto)


@mod.route('/chef/<int:id>', methods=['GET'])
def get_photo(id):
    get_photo(id, ChefPhoto)


@mod.route('/chef/', methods=['GET'])
def get_all_photos():
    get_all_photos(ChefPhoto)


@mod.route('/chef/<int:id>', methods=['DELETE'])
def delete_photo(id):
    delete_photo(id, ChefPhoto)

# ToolPhoto

@mod.route('/tool', methods=['POST'])
def new_photo():
    new_photo(ToolPhoto)

@mod.route('/tool/<int:id>', methods=['PUT'])
def update_photo(id):
    update_photo(id, ToolPhoto)


@mod.route('/tool/<int:id>', methods=['GET'])
def get_photo(id):
    get_photo(id, ToolPhoto)


@mod.route('/tool/', methods=['GET'])
def get_all_photos():
    get_all_photos(ToolPhoto)


@mod.route('/tool/<int:id>', methods=['DELETE'])
def delete_photo(id):
    delete_photo(id, ToolPhoto)

# SchoolPhoto

@mod.route('/school', methods=['POST'])
def new_photo():
    new_photo(SchoolPhoto)

@mod.route('/school/<int:id>', methods=['PUT'])
def update_photo(id):
    update_photo(id, SchoolPhoto)


@mod.route('/school/<int:id>', methods=['GET'])
def get_photo(id):
    get_photo(id, SchoolPhoto)


@mod.route('/school/', methods=['GET'])
def get_all_photos():
    get_all_photos(SchoolPhoto)


@mod.route('/school/<int:id>', methods=['DELETE'])
def delete_photo(id):
    delete_photo(id, SchoolPhoto)