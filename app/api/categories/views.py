from flask import Blueprint, jsonify, request

from app.api import db
from app.api.helpers import response_builder
from app.api.categories.model import Category

mod = Blueprint('categories', __name__, url_prefix='/api/categories')


# {"title":"good"}
@mod.route('/', methods=['POST'])
def new_category():
    title = request.json.get('title')
    if title is None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    category = Category(title=title)
    db.session.add(category)
    db.session.commit()
    information = response_builder(category, Category)
    return jsonify({'error_code': 201, 'result': information}), 201


@mod.route('/<int:id>', methods=['PUT'])
def update_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    if request.json.get('title'):
        category.title = request.json.get('title')
    db.session.commit()
    category = Category.query.get(id)
    information = response_builder(category, Category)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/<int:id>', methods=['GET'])
def get_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # category with `id` isn't exist
    information = response_builder(category, Category)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/', methods=['GET'])
def get_all_categories():
    categories = []
    for category in Category.query.all():
        information = response_builder(category, Category)
        categories.append(information)
    return jsonify({'error_code': 200, 'result': categories}), 200


@mod.route('/<int:id>', methods=['DELETE'])
def delete_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # category with `id` isn't exist
    db.session.delete(category)
    db.session.commit()
    return jsonify({'error_code': 200}), 200