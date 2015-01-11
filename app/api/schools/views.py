from flask import request, jsonify, g, url_for, Blueprint
from flask.ext.login import login_required

from app.api import db, auto
from app.api.constants import OK, BAD_REQUEST
from app.api.helpers import *
from app.api.schools.model import *
from app.decorators import admin_required


mod = Blueprint('schools', __name__, url_prefix='/api/schools')


@auto.doc()
@mod.route('/', methods=['POST'])
@login_required
@admin_required
def new_school():
    """
    Add new school. List of parameters in json request:
            title (required)
    Example of request:
            {"title":"good"}
    :return: json with parameters:
            error_code - server response_code
            result - information about created school
    """
    title = request.json.get('title')
    if title is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    school = School(title=title)
    db.session.add(school)
    db.session.commit()
    information = response_builder(school, School)
    return jsonify({'error_code': OK, 'result': information}), 201


@auto.doc()
@mod.route('/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_school(id):
    """
    Update exists school. List of parameters in json request:
            title (optional)
    Example of request:
            {"title":"good"}
    :param id: school id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated school
    """
    school = School.query.get(id)
    if not school:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    if request.json.get('title'):
        school.title = request.json.get('title')
    db.session.commit()
    school = School.query.get(id)
    information = response_builder(school, School)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
def get_school(id):
    """
    Get information about school.
    :param id: school id
    :return: json with parameters:
            error_code - server response_code
            result - information about school
    """
    school = School.query.get(id)
    if not school:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # school with `id` isn't exist
    information = response_builder(school, School)
    information['photos'] = []
    for photo in SchoolPhoto.query.filter_by(item_id=school.id):
        photo_information = response_builder(photo, SchoolPhoto)
        information['photos'].append(photo_information)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
def get_all_schools():
    """
    Get information about all exist schools.
    :return: json with parameters:
            error_code - server response_code
            result - information about schools
    """
    schools = []
    for school in School.query.all():
        information = response_builder(school, School)
        schools.append(information)
    return jsonify({'error_code': OK, 'result': schools}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_school(id):
    """
    Delete school.
    :param id: school id
    :return: json with parameters:
            error_code - server response_code
    """
    school = School.query.get(id)
    if not school:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # school with `id` isn't exist
    db.session.delete(school)
    db.session.commit()
    return jsonify({'error_code': OK}), 200


@auto.doc()
@mod.route('/item/', methods=['POST'])
@login_required
@admin_required
def new_school_item():
    """
    Add new school item. List of parameters in json request:
            school_id (required)
            step_number (required)
            description (optional)
    Example of request:
            {"school_id":1, "step_number":1, "description":"erererr"}
    :return: json with parameters:
            error_code - server response_code
            result - information about created school item
    """
    school_id = request.json.get('school_id')
    step_number = request.json.get('step_number')
    description = request.json.get('description')
    photo = request.json.get('photo')
    if school_id is None or step_number is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    school_item = SchoolItem(school_id=school_id, step_number=step_number, description=description, photo=photo)
    db.session.add(school_item)
    db.session.commit()
    information = response_builder(school_item, SchoolItem)
    return jsonify({'error_code': 201, 'result': information}), 201


@auto.doc()
@mod.route('/item/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_school_item(id):
    """
    Update exists school item. List of parameters in json request:
            school_id (optional)
            step_number (optional)
            description (optional)
    Example of request:
            {"school_id":1, "step_number":1, "description":"trololo"}
    :param id: school item id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated school item
    """
    school_item = SchoolItem.query.get(id)
    if not school_item:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
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
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/item/<int:id>', methods=['GET'])
def get_school_item(id):
    """
    Get information about school item.
    :param id: school item id
    :return: json with parameters:
            error_code - server response_code
            result - information about school item
    """
    school_item = SchoolItem.query.get(id)
    if not school_item:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # school_item with `id` isn't exist
    information = response_builder(school_item, SchoolItem)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/item/', methods=['GET'])
def get_all_school_items():
    """
    Get information about all exist school items.
    :return: json with parameters:
            error_code - server response_code
            result - information about school items
    """
    school_items = []
    for school_item in SchoolItem.query.all():
        information = response_builder(school_item, SchoolItem)
        school_items.append(information)
    return jsonify({'error_code': OK, 'result': school_items}), 200


@auto.doc()
@mod.route('/item/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_school_item(id):
    """
    Delete school item.
    :param id: school item id
    :return: json with parameters:
            error_code - server response_code
    """
    school_item = SchoolItem.query.get(id)
    if not school_item:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # school_item with `id` isn't exist
    db.session.delete(school_item)
    db.session.commit()
    return jsonify({'error_code': OK}), 200


@auto.doc()
@mod.route('/fullitem/<int:id>', methods=['GET'])
def get_one_school_items(id):
    """
    Get information about all school items for school with special id.
    :param id: school id
    :return: json with parameters:
            error_code - server response_code
            result - information about school items
    """
    school_items = []
    for school_item in SchoolItem.query.filter_by(school_id=id):
        information = response_builder(school_item, SchoolItem)
        school_items.append(information)
    return jsonify({'error_code': OK, 'result': school_items}), 200
