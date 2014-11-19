from flask import request, jsonify, g, url_for, Blueprint

from app.api import db
from app.api.helpers import *
from app.api.tools.model import Tool


mod = Blueprint('tools', __name__, url_prefix='/api/tools')


# {"title":"good", "description":"ooooo"}
@mod.route('/', methods=['POST'])
def new_tool():
    title = request.json.get('title')
    description = request.json.get('description')
    if title is None or description is None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    tool = Tool(title=title, description=description)
    db.session.add(tool)
    db.session.commit()
    information = response_builder(tool, Tool)
    return jsonify({'error_code': 201, 'result': information}), 201


@mod.route('/<int:id>', methods=['PUT'])
def update_tool(id):
    tool = Tool.query.get(id)
    if not tool:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    if request.json.get('title'):
        tool.title = request.json.get('title')
    if request.json.get('description'):
        tool.description = request.json.get('description')
    db.session.commit()
    tool = Tool.query.get(id)
    information = response_builder(tool, Tool)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/<int:id>', methods=['GET'])
def get_tool(id):
    tool = Tool.query.get(id)
    if not tool:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # tool with `id` isn't exist
    information = response_builder(tool, Tool)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/', methods=['GET'])
def get_all_tools():
    tools = []
    for tool in Tool.query.all():
        information = response_builder(tool, Tool)
        tools.append(information)
    return jsonify({'error_code': 200, 'result': tools}), 200


@mod.route('/<int:id>', methods=['DELETE'])
def delete_tool(id):
    tool = Tool.query.get(id)
    if not tool:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # tool with `id` isn't exist
    db.session.delete(tool)
    db.session.commit()
    return jsonify({'error_code': 200}), 200