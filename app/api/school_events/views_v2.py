from flask import request, jsonify, g, url_for, Blueprint
from flask.ext.login import login_required

from app.api import db, auto
from app.api.constants import OK, BAD_REQUEST
from app.api.helpers import *
from app.api.school_events.model import *
from app.decorators import admin_required


mod = Blueprint('school_events_v2', __name__, url_prefix='/api_v2/school_events')


@auto.doc()
@mod.route('/', methods=['POST'])
@login_required
@admin_required
def new_school_event():
    """
    Add new school event. List of parameters in json request:
            date (required)
            price (required)
            school_id (required)
            places_all (required)
            places_left (required)
            description (optional)
            url (optional)
    :return: json with parameters:
            error_code - server response_code
            result - information about created school event
    """
    date = request.json.get('school_id')
    price = request.json.get('school_id')
    school_id = request.json.get('school_id')
    places_all = request.json.get('school_id')
    places_left = request.json.get('school_id')
    description = request.json.get('description')
    url = request.json.get('url')
    if school_id is None or date is None or price is None or places_all is None or places_left is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    school_event = SchoolEvent(date=date, price=price, school_id=school_id, places_all=places_all,
                               places_left=places_left, description=description, url=url)
    db.session.add(school_event)
    db.session.commit()
    information = response_builder(school_event, SchoolEvent)
    return jsonify({'error_code': 201, 'result': information}), 201


@auto.doc()
@mod.route('/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_school_event(id):
    """
    Update exists school event. List of parameters in json request:
            date (optional)
            price (optional)
            school_id (optional)
            places_all (optional)
            places_left (optional)
            description (optional)
            url (optional)
    :param id: school event id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated school event
    """
    school_event = SchoolEvent.query.get(id)
    if not school_event:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    if request.json.get('school_id'):
        school_event.school_id = request.json.get('school_id')
    if request.json.get('date'):
        school_event.date = request.json.get('date')
    if request.json.get('description'):
        school_event.description = request.json.get('description')
    if request.json.get('price'):
        school_event.price = request.json.get('price')
    if request.json.get('places_all'):
        school_event.places_all = request.json.get('places_all')
    if request.json.get('places_left'):
        school_event.places_left = request.json.get('places_left')
    if request.json.get('url'):
        school_event.url = request.json.get('url')
    db.session.commit()
    school_event = SchoolEvent.query.get(id)
    information = response_builder(school_event, SchoolEvent)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
def get_school_event(id):
    """
    Get information about school event.
    :param id: school event id
    :return: json with parameters:
            error_code - server response_code
            result - information about school event
    """
    school_event = SchoolEvent.query.get(id)
    if not school_event:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # school_item with `id` isn't exist
    information = response_builder(school_event, SchoolEvent)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
def get_all_school_events():
    """
    Get information about all exist school events.
    :return: json with parameters:
            error_code - server response_code
            result - information about school events
    """
    school_events = []
    for school_event in SchoolEvent.query.all():
        information = response_builder(school_event, SchoolEvent)
        school_events.append(information)
    return jsonify({'error_code': OK, 'result': school_events}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_school_event(id):
    """
    Delete school event.
    :param id: school event id
    :return: json with parameters:
            error_code - server response_code
    """
    school_event = SchoolEvent.query.get(id)
    if not school_event:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # school_event with `id` isn't exist
    db.session.delete(school_event)
    db.session.commit()
    return jsonify({'error_code': OK}), 200


@auto.doc()
@mod.route('/add_for_me/<int:event_id>')
@login_required
def add_school_event_for_user(event_id):
    """
    Add school event for current user.
    :param event_id: event id
    :return: json with parameters:
            error_code - server response_code
    """
    school_event = SchoolEvent.query.get(event_id)
    if not school_event:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # school_event with `id` isn't exist
    current_user.school_events.append(school_event)
    db.session.commit()
    return jsonify({'error_code': OK}), 200


@auto.doc()
@mod.route('/delete_for_me/<int:event_id>')
@login_required
def delete_school_event_for_user(event_id):
    """
    Delete school event for current user.
    :param event_id: event id
    :return: json with parameters:
            error_code - server response_code
    """
    school_event = SchoolEvent.query.get(event_id)
    if not school_event:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # school_event with `id` isn't exist
    current_user.school_events.remove(school_event)
    db.session.commit()
    return jsonify({'error_code': OK}), 200


@auto.doc()
@mod.route('/get_for_me/')
@login_required
def get_school_events_for_user():
    """
    Get school events for current user.
    :return: json with parameters:
            error_code - server response_code
            result - information about school events
    """
    school_events = []
    for school_event in current_user.school_events:
        school_events.append(school_event.id)
    information = []
    if school_events is not None:
        for school_event_id in school_events:
            school_event = SchoolEvent.query.get(school_event_id)
            school_event_information = response_builder(school_event, SchoolEvent)
            information.append(school_event_information)
    return jsonify({'error_code': OK, 'result': information}), 200