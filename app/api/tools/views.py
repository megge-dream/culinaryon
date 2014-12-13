from flask import request, jsonify, g, url_for, Blueprint
from flask.ext.login import login_required

from app.api import db, auto
from app.api.constants import BAD_REQUEST, OK
from app.api.helpers import *
from app.api.tools.model import Tool
from app.decorators import admin_required


mod = Blueprint('tools', __name__, url_prefix='/api/tools')


@auto.doc()
@mod.route('/', methods=['POST'])
@login_required
@admin_required
def new_tool():
    """
    Add new tool. List of parameters in json request:
            title (required)
            description (required)
    Example of request:
            {"title":"good", "description":"smth smart"}
    :return: json with parameters:
            error_code - server response_code
            result - information about created tool
    """
    title = request.json.get('title')
    description = request.json.get('description')
    if title is None or description is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    tool = Tool(title=title, description=description)
    db.session.add(tool)
    db.session.commit()
    information = response_builder(tool, Tool)
    return jsonify({'error_code': OK, 'result': information}), 201


@auto.doc()
@mod.route('/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_tool(id):
    """
    Update exists tool. List of parameters in json request:
            title (optional)
            description (optional)
    Example of request:
            {"title":"good"}
    :param id: tool id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated tool
    """
    tool = Tool.query.get(id)
    if not tool:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    if request.json.get('title'):
        tool.title = request.json.get('title')
    if request.json.get('description'):
        tool.description = request.json.get('description')
    db.session.commit()
    tool = Tool.query.get(id)
    information = response_builder(tool, Tool)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
@login_required
def get_tool(id):
    """
    Get information about tool.
    :param id: tool id
    :return: json with parameters:
            error_code - server response_code
            result - information about tool
    """
    tool = Tool.query.get(id)
    if not tool:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # tool with `id` isn't exist
    information = response_builder(tool, Tool)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
@login_required
def get_all_tools():
    """
    Get information about all exist tools.
    :return: json with parameters:
            error_code - server response_code
            result - information about tools
    """
    tools = []
    for tool in Tool.query.all():
        information = response_builder(tool, Tool)
        tools.append(information)
    return jsonify({'error_code': OK, 'result': tools}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_tool(id):
    """
    Delete tool.
    :param id: tool id
    :return: json with parameters:
            error_code - server response_code
    """
    tool = Tool.query.get(id)
    if not tool:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # tool with `id` isn't exist
    db.session.delete(tool)
    db.session.commit()
    return jsonify({'error_code': OK}), 200