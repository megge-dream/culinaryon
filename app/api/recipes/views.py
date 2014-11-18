from flask import request, jsonify, g, url_for, Blueprint

from app.api import db, auth
from app.api.helpers import *
from app.api.recipes.model import Recipe, InstructionItem


mod = Blueprint('recipes', __name__, url_prefix='/api/recipes')


# {"title":"good"}
@mod.route('/', methods=['POST'])
def new_recipe():
    title = request.json.get('title')
    description = request.json.get('description')
    spicy = request.json.get('spicy')
    complexity = request.json.get('complexity')
    time = request.json.get('time')
    amount_of_persons = request.json.get('amount_of_persons')
    chef_id = request.json.get('chef_id')
    video = request.json.get('video')
    if title is None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    recipe = Recipe(title=title, description=description, spicy=spicy, complexity=complexity, time=time,
                    amount_of_persons=amount_of_persons, chef_id=chef_id, video=video)
    db.session.add(recipe)
    db.session.commit()
    information = response_builder(recipe, Recipe)
    return jsonify({'error_code': 201, 'result': information}), 201


@mod.route('/<int:id>', methods=['PUT'])
def update_recipe(id):
    recipe = Recipe.query.get(id)
    if not recipe:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    if request.json.get('title'):
        recipe.title = request.json.get('title')
    if request.json.get('description'):
        recipe.description = request.json.get('description')
    if request.json.get('spicy'):
        recipe.spicy = request.json.get('spicy')
    if request.json.get('complexity'):
        recipe.complexity = request.json.get('complexity')
    if request.json.get('time'):
        recipe.time = request.json.get('time')
    if request.json.get('amount_of_persons'):
        recipe.amount_of_persons = request.json.get('amount_of_persons')
    if request.json.get('chef_id'):
        recipe.recipe_id = request.json.get('chef_id')
    if request.json.get('video'):
        recipe.recipe_id = request.json.get('video')
    db.session.commit()
    recipe = Recipe.query.get(id)
    information = response_builder(recipe, Recipe)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/<int:id>', methods=['GET'])
def get_recipe(id):
    recipe = Recipe.query.get(id)
    if not recipe:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # recipe with `id` isn't exist
    information = response_builder(recipe, Recipe)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/', methods=['GET'])
def get_all_recipes():
    recipes = []
    for recipe in Recipe.query.all():
        information = response_builder(recipe, Recipe)
        recipes.append(information)
    return jsonify({'error_code': 200, 'result': recipes}), 200


@mod.route('/<int:id>', methods=['DELETE'])
def delete_recipe(id):
    recipe = Recipe.query.get(id)
    if not recipe:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # recipe with `id` isn't exist
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({'error_code': 200}), 200


# {"title":"good"}
@mod.route('/instruction/', methods=['POST'])
def new_instruction():
    recipe_id = request.json.get('recipe_id')
    step_number = request.json.get('step_number')
    time = request.json.get('time')
    photo = request.json.get('photo')
    description = request.json.get('description')
    video = request.json.get('video')
    if recipe_id is None or step_number is None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    instruction = InstructionItem(recipe_id=recipe_id, step_number=step_number, time=time, photo=photo, description=description,
                                  video=video)
    db.session.add(instruction)
    db.session.commit()
    information = response_builder(instruction, InstructionItem)
    return jsonify({'error_code': 201, 'result': information}), 201


@mod.route('/instruction/<int:id>', methods=['PUT'])
def update_instruction(id):
    recipe = InstructionItem.query.get(id)
    if not recipe:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    if request.json.get('recipe_id'):
        recipe.recipe_id = request.json.get('recipe_id')
    if request.json.get('description'):
        recipe.description = request.json.get('description')
    if request.json.get('step_number'):
        recipe.step_number = request.json.get('step_number')
    if request.json.get('photo'):
        recipe.photo = request.json.get('photo')
    if request.json.get('time'):
        recipe.time = request.json.get('time')
    if request.json.get('video'):
        recipe.recipe_id = request.json.get('video')
    db.session.commit()
    instruction = InstructionItem.query.get(id)
    information = response_builder(instruction, InstructionItem)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/instruction/<int:id>', methods=['GET'])
def get_instruction(id):
    instruction = InstructionItem.query.get(id)
    if not instruction:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # instruction with `id` isn't exist
    information = response_builder(instruction, InstructionItem)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/instruction/', methods=['GET'])
def get_all_instructions():
    instructions = []
    for instruction in InstructionItem.query.all():
        information = response_builder(instruction, InstructionItem)
        instructions.append(information)
    return jsonify({'error_code': 200, 'result': instructions}), 200


@mod.route('/instruction/<int:id>', methods=['DELETE'])
def delete_instruction(id):
    instruction = InstructionItem.query.get(id)
    if not instruction:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # instruction with `id` isn't exist
    db.session.delete(instruction)
    db.session.commit()
    return jsonify({'error_code': 200}), 200