# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from flask.ext.login import login_required

from app.api import db, auto
from app.api.constants import OK, BAD_REQUEST
from app.api.helpers import response_builder
from app.api.type_of_grape.model import TypeOfGrape
from app.decorators import admin_required

mod = Blueprint('type_of_grape_v2', __name__, url_prefix='/api_v2/type_of_grape')


@auto.doc()
@mod.route('/', methods=['POST'])
@login_required
@admin_required
def new_type_of_grape():
    """
    Add new type_of_grape. List of parameters in json request:
            title (required)
            photo (optional)
    Example of request:
            {"title":"good"}
    :return: json with parameters:
            error_code - server response_code
            result - information about created type_of_grape
    """
    title = request.json.get('title')
    photo = request.json.get('photo')
    if title is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    type_of_grape = TypeOfGrape(title=title, photo=photo)
    db.session.add(type_of_grape)
    db.session.commit()
    information = response_builder(type_of_grape, TypeOfGrape)
    return jsonify({'error_code': OK, 'result': information}), 201


@auto.doc()
@mod.route('/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_type_of_grape(id):
    """
    Update exists type_of_grape. List of parameters in json request:
            title (optional)
            photo (optional)
    Example of request:
            {"title":"good"}
    :param id: type_of_grape id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated type_of_grape
    """
    type_of_grape = TypeOfGrape.query.get(id)
    if not type_of_grape:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    if request.json.get('title'):
        type_of_grape.title = request.json.get('title')
    if request.json.get('photo'):
        type_of_grape.photo = request.json.get('photo')
    db.session.commit()
    type_of_grape = TypeOfGrape.query.get(id)
    information = response_builder(type_of_grape, TypeOfGrape)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
def get_type_of_grape(id):
    """
    Get information about type_of_grape.
    :param id: type_of_grape id
    :return: json with parameters:
            error_code - server response_code
            result - information about type_of_grape
    """
    type_of_grape = TypeOfGrape.query.get(id)
    if not type_of_grape:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # type_of_grape with `id` isn't exist
    information = response_builder(type_of_grape, TypeOfGrape)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
def get_all_type_of_grapes():
    """
    Get information about all exist type_of_grapes.
    :return: json with parameters:
            error_code - server response_code
            result - information about type_of_grapes
    """
    type_of_grapes = []
    for type_of_grape in TypeOfGrape.query.all():
        information = response_builder(type_of_grape, TypeOfGrape)
        type_of_grapes.append(information)
    ids = []
    type_of_grapes_ids = TypeOfGrape.query.all()
    for type_of_grape_id in type_of_grapes_ids:
        ids.append(type_of_grape_id.id)
    return jsonify({'error_code': OK, 'result': type_of_grapes, 'ids': ids}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_type_of_grape(id):
    """
    Delete type_of_grape.
    :param id: type_of_grape id
    :return: json with parameters:
            error_code - server response_code
    """
    type_of_grape = TypeOfGrape.query.get(id)
    if not type_of_grape:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # category with `id` isn't exist
    db.session.delete(type_of_grape)
    db.session.commit()
    return jsonify({'error_code': OK}), 200