# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from flask.ext.login import login_required

from app.api import db, auto
from app.api.constants import OK, BAD_REQUEST
from app.api.helpers import response_builder
from app.api.categories.model import Category
from app.decorators import admin_required

mod = Blueprint('categories', __name__, url_prefix='/api/categories')


@auto.doc()
@mod.route('/', methods=['POST'])
@login_required
@admin_required
def new_category():
    """
    Add new category. List of parameters in json request:
            title (required)
    Example of request:
            {"title":"good"}
    :return: json with parameters:
            error_code - server response_code
            result - information about created category
    """
    title = request.json.get('title')
    if title is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    category = Category(title=title)
    db.session.add(category)
    db.session.commit()
    information = response_builder(category, Category)
    return jsonify({'error_code': OK, 'result': information}), 201


@auto.doc()
@mod.route('/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_category(id):
    """
    Update exists category. List of parameters in json request:
            title (optional)
    Example of request:
            {"title":"good"}
    :param id: category id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated category
    """
    category = Category.query.get(id)
    if not category:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    if request.json.get('title'):
        category.title = request.json.get('title')
    db.session.commit()
    category = Category.query.get(id)
    information = response_builder(category, Category)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
@login_required
def get_category(id):
    """
    Get information about category.
    :param id: category id
    :return: json with parameters:
            error_code - server response_code
            result - information about category
    """
    category = Category.query.get(id)
    if not category:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # category with `id` isn't exist
    information = response_builder(category, Category)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
@login_required
def get_all_categories():
    """
    Get information about all exist categories.
    :return: json with parameters:
            error_code - server response_code
            result - information about categories
    """
    categories = []
    for category in Category.query.all():
        information = response_builder(category, Category)
        categories.append(information)
    return jsonify({'error_code': OK, 'result': categories}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_category(id):
    """
    Delete category.
    :param id: category id
    :return: json with parameters:
            error_code - server response_code
    """
    category = Category.query.get(id)
    if not category:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # category with `id` isn't exist
    db.session.delete(category)
    db.session.commit()
    return jsonify({'error_code': OK}), 200