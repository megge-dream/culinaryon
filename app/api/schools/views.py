from flask import request, jsonify, g, url_for, Blueprint

from app.api import db, auth
from app.api.helpers import *
from app.api.schools.model import *


mod = Blueprint('schools', __name__, url_prefix='/api/schools')


# {"title":"good"}
@mod.route('/', methods=['POST'])
def new_school():
    title = request.json.get('title')
    if title is None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    school = School(title=title)
    db.session.add(school)
    db.session.commit()
    information = response_builder(school, School)
    return jsonify({'error_code': 201, 'result': information}), 201


@mod.route('/<int:id>', methods=['PUT'])
def update_school(id):
    school = School.query.get(id)
    if not school:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    if request.json.get('title'):
        school.title = request.json.get('title')
    db.session.commit()
    school = School.query.get(id)
    information = response_builder(school, School)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/<int:id>', methods=['GET'])
def get_school(id):
    school = School.query.get(id)
    if not school:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # school with `id` isn't exist
    information = response_builder(school, School)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/', methods=['GET'])
def get_all_schools():
    schools = []
    for school in School.query.all():
        information = response_builder(school, School)
        schools.append(information)
    return jsonify({'error_code': 200, 'result': schools}), 200


@mod.route('/<int:id>', methods=['DELETE'])
def delete_school(id):
    school = School.query.get(id)
    if not school:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # school with `id` isn't exist
    db.session.delete(school)
    db.session.commit()
    return jsonify({'error_code': 200}), 200


# {"title":"good"}
@mod.route('/item/', methods=['POST'])
def new_school_item():
    school_id = request.json.get('school_id')
    step_number = request.json.get('step_number')
    description = request.json.get('description')
    photo = request.json.get('photo')
    if school_id is None or step_number is None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    school_item = SchoolItem(school_id=school_id, step_number=step_number, description=description, photo=photo)
    db.session.add(school_item)
    db.session.commit()
    information = response_builder(school_item, SchoolItem)
    return jsonify({'error_code': 201, 'result': information}), 201


@mod.route('/item/<int:id>', methods=['PUT'])
def update_school_item(id):
    school_item = SchoolItem.query.get(id)
    if not school_item:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    if request.json.get('school_id'):
        school_item.school_id = request.json.get('school_id')
    if request.json.get('step_number'):
        school_item.step_number = request.json.get('step_number')
    if request.json.get('description'):
        school_item.description = request.json.get('description')
    if request.json.get('photo'):
        school_item.photo = request.json.get('photo')
    db.session.commit()
    school_item = SchoolItem.query.get(id)
    information = response_builder(school_item, SchoolItem)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/item/<int:id>', methods=['GET'])
def get_school_item(id):
    school_item = SchoolItem.query.get(id)
    if not school_item:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # school_item with `id` isn't exist
    information = response_builder(school_item, SchoolItem)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/item/', methods=['GET'])
def get_all_school_items():
    school_items = []
    for school_item in SchoolItem.query.all():
        information = response_builder(school_item, SchoolItem)
        school_items.append(information)
    return jsonify({'error_code': 200, 'result': school_items}), 200


@mod.route('/item/<int:id>', methods=['DELETE'])
def delete_school_item(id):
    school_item = SchoolItem.query.get(id)
    if not school_item:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # school_item with `id` isn't exist
    db.session.delete(school_item)
    db.session.commit()
    return jsonify({'error_code': 200}), 200