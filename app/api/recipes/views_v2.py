from flask import request, jsonify, g, url_for, Blueprint
from flask.ext.login import login_required
from sqlalchemy import distinct

from app.api import db, auto
from app.api.categories.model import Category
from app.api.constants import OK, BAD_REQUEST
from app.api.cuisine_types.model import CuisineType
from app.api.helpers import *
from app.api.ingredients.model import Ingredient
from app.api.likes.model import Like
from app.api.photos.model import RecipePhoto
from app.api.recipes.model import Recipe, InstructionItem
from app.api.sets.model import Set, UserSet
from app.api.tools.model import Tool
from app.api.users.constants import FOREVER, MONTH, PUBLISHED
from app.api.wines.model import Wine
from app.api.wines.views_v2 import wine_response_builder
from app.decorators import admin_required


mod = Blueprint('recipes_v2', __name__, url_prefix='/api_v2/recipes')


@auto.doc()
@mod.route('/', methods=['POST'])
@login_required
@admin_required
def new_recipe():
    """
    Add new recipe. List of parameters in json request:
            title (required)
            chef_id (optional)
            description (optional)
            spicy (optional)
            complexity (optional)
            time (optional)
            amount_of_persons (optional)
            video (optional)
            categories (optional)
            cuisine_types (optional)
            tools (optional)
            wines (optional)
            set_id (optional)
    Example of request:
            {"title":"good", "chef_id":1, "cuisine_types":[1,2]}
    :return: json with parameters:
            error_code - server response_code
            result - information about created recipe
    """
    title = request.json.get('title')
    description = request.json.get('description')
    spicy = request.json.get('spicy')
    complexity = request.json.get('complexity')
    time = request.json.get('time')
    amount_of_persons = request.json.get('amount_of_persons')
    chef_id = request.json.get('chef_id')
    video = request.json.get('video')
    categories = request.json.get('categories')
    cuisine_types = request.json.get('cuisine_types')
    tools = request.json.get('tools')
    wines = request.json.get('wines')
    set_id = request.json.get('set_id')
    if title is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    recipe = Recipe(title=title, description=description, spicy=spicy, complexity=complexity, time=time,
                    amount_of_persons=amount_of_persons, chef_id=chef_id, video=video, set_id=set_id)
    db.session.add(recipe)
    db.session.commit()
    insert_recipes_many_to_many(recipe, categories, cuisine_types, tools, wines)
    information = recipe_response_builder(recipe)
    return jsonify({'error_code': OK, 'result': information}), 201


@auto.doc()
@mod.route('/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_recipe(id):
    """
    Update exists recipe. List of parameters in json request:
            title (optional)
            chef_id (optional)
            description (optional)
            spicy (optional)
            complexity (optional)
            time (optional)
            amount_of_persons (optional)
            video (optional)
            categories (optional)
            cuisine_types (optional)
            tools (optional)
            wines (optional)
            set_id (optional)
    Example of request:
            {"title":"good", "chef_id":1, "cuisine_types":[1]}
    :param id: recipe id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated recipe
    """
    recipe = Recipe.query.get(id)
    if not recipe:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
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
        recipe.chef_id = request.json.get('chef_id')
    if request.json.get('video'):
        recipe.video = request.json.get('video')
    if request.json.get('set_id'):
        recipe.set_id = request.json.get('set_id')
    categories = request.json.get('categories')
    cuisine_types = request.json.get('cuisine_types')
    tools = request.json.get('tools')
    wines = request.json.get('wines')
    db.session.commit()
    insert_recipes_many_to_many(recipe, categories, cuisine_types, tools, wines)
    recipe = Recipe.query.get(id)
    information = recipe_response_builder(recipe)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_recipe(id):
    """
    Delete recipe.
    :param id: recipe id
    :return: json with parameters:
            error_code - server response_code
    """
    recipe = Recipe.query.get(id)
    if not recipe:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # recipe with `id` isn't exist
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({'error_code': OK}), 200


@auto.doc()
@mod.route('/instruction/', methods=['POST'])
@login_required
@admin_required
def new_instruction():
    """
    Add new instruction. List of parameters in json request:
            title (required)
            step_number (required)
            recipe_id (optional)
            time (optional)
            photo (optional)
            description (optional)
            video (optional)
    Example of request:
            {"recipe_id":1, "step_number":1, "description":"qwertyu"}
    :return: json with parameters:
            error_code - server response_code
            result - information about created instruction
    """
    recipe_id = request.json.get('recipe_id')
    step_number = request.json.get('step_number')
    time = request.json.get('time')
    photo = request.json.get('photo')
    description = request.json.get('description')
    video = request.json.get('video')
    if recipe_id is None or step_number is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    instruction = InstructionItem(recipe_id=recipe_id, step_number=step_number, time=time, photo=photo, description=description,
                                  video=video)
    db.session.add(instruction)
    db.session.commit()
    information = response_builder(instruction, InstructionItem)
    return jsonify({'error_code': OK, 'result': information}), 201


@auto.doc()
@mod.route('/instruction/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_instruction(id):
    """
    Update exists instruction. List of parameters in json request:
            title (optional)
            step_number (optional)
            recipe_id (optional)
            time (optional)
            photo (optional)
            description (optional)
            video (optional)
    Example of request:
            {"recipe_id":1, "step_number":1, "description":"qwertyu"}
    :param id: instruction id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated instruction
    """
    recipe = InstructionItem.query.get(id)
    if not recipe:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
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
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/instruction/<int:id>', methods=['GET'])
def get_instruction(id):
    """
    Get information about instruction.
    :param id: instruction id
    :return: json with parameters:
            error_code - server response_code
            result - information about instruction
    """
    instruction = InstructionItem.query.get(id)
    if not instruction:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # instruction with `id` isn't exist
    information = response_builder(instruction, InstructionItem)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/instruction/', methods=['GET'])
def get_all_instructions():
    """
    Get information about all exist instructions.
    :return: json with parameters:
            error_code - server response_code
            result - information about instructions
    """
    instructions = []
    for instruction in InstructionItem.query.all():
        information = response_builder(instruction, InstructionItem)
        instructions.append(information)
    return jsonify({'error_code': OK, 'result': instructions}), 200


@auto.doc()
@mod.route('/instruction/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_instruction(id):
    """
    Delete instruction.
    :param id: instruction id
    :return: json with parameters:
            error_code - server response_code
    """
    instruction = InstructionItem.query.get(id)
    if not instruction:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # instruction with `id` isn't exist
    db.session.delete(instruction)
    db.session.commit()
    return jsonify({'error_code': OK}), 200


@auto.doc()
@mod.route('/fullinstruction/<int:id>', methods=['GET'])
def get_recipe_instructions(id):
    """
    Get information about all instructions for recipe with special id.
    :param id: recipe id
    :return: json with parameters:
            error_code - server response_code
            result - information about instructions
    """
    instructions = []
    for instruction in InstructionItem.query.filter_by(recipe_id=id):
        information = response_builder(instruction, InstructionItem, excluded=["recipe_id"])
        instructions.append(information)
    return jsonify({'error_code': OK, 'result': instructions}), 200


def insert_recipes_many_to_many(recipe, categories, cuisine_types, tools, wines):
    if categories is not None:
        for category_id in categories:
            category = Category.query.get(category_id)
            recipe.categories.append(category)
            db.session.commit()
    if cuisine_types is not None:
        for cuisine_type_id in cuisine_types:
            cuisine_type = CuisineType.query.get(cuisine_type_id)
            recipe.cuisine_types.append(cuisine_type)
            db.session.commit()
    if tools is not None:
        for tool_id in tools:
            tool = Tool.query.get(tool_id)
            recipe.tools.append(tool)
            db.session.commit()
    if wines is not None:
        for wine_id in wines:
            wine = Wine.query.get(wine_id)
            recipe.wines.append(wine)
            db.session.commit()


@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
def get_recipe(id):
    """
    Get information about recipe.
    :param id: recipe id
    :return: json with parameters:
            error_code - server response_code
            result - information about recipe
    """
    recipe = Recipe.query.get(id)
    if not recipe:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # recipe with `id` isn't exist
    information = recipe_response_builder(recipe)
    information['ingredients'] = get_ingredients_by_divisions(id)
    hash_of_information = make_hash(information)
    information['hash'] = hash_of_information
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
def get_all_recipes_sets_wines():
    """
    Get information about all exist recipes, sets and wines.
    :param offset (GET param) : starts from which object in every entity
    :param limit (GET param) : how many object you want to get in every entity
    :return: json with parameters:
            error_code - server response_code
            result_recipes - information about recipes
            result_sets - information about sets
            result_wines - information about wines
            entities_count - numbers of biggest object
            recipes_ids - ids of all recipes
            sets_ids - ids of all sets
            wines_ids - ids of all wines
    """
    recipes = []
    sets = []
    wines = []
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', type=int)
    count = [Recipe.query.count(), Set.query.count(), Wine.query.count()]
    count = max(count)
    if current_user.is_authenticated() and current_user.role_code == 0:
        recipe_query = Recipe.query
    else:
        recipe_query = Recipe.query.filter_by(type=PUBLISHED)
    if limit is not None and offset is not None:
        # for faster loading
        limit = 5
        recipes_band = recipe_query.slice(start=offset, stop=limit+offset).all()
        sets_band = Set.query.slice(start=offset, stop=limit+offset).all()
        wines_band = Wine.query.slice(start=offset, stop=limit+offset).all()
    else:
        recipes_band = recipe_query.all()
        sets_band = Set.query.all()
        wines_band = Wine.query.all()
    for recipe in recipes_band:
        information = recipe_response_builder(recipe)
        information['ingredients'] = get_ingredients_by_divisions(recipe.id)
        hash_of_information = make_hash(information)
        information['hash'] = hash_of_information
        recipes.append(information)
    recipes_ids = []
    recipes_all = recipe_query.all()
    for recipe in recipes_all:
        recipes_ids.append(recipe.id)
    for set in sets_band:
        information = set_response_builder(set)
        sets.append(information)
    sets_ids = []
    sets_all = Set.query.all()
    for set in sets_all:
        sets_ids.append(set.id)
    for wine in wines_band:
        information = response_builder(wine, Wine)
        wines.append(information)
    wines_ids = []
    wines_all = Wine.query.all()
    for wine in wines_all:
        wines_ids.append(wine.id)
    return jsonify({'error_code': OK, 'result_recipes': recipes, 'result_sets': sets, 'result_wines': wines,
                    'entities_count': count, 'recipes_ids': recipes_ids, 'sets_ids': sets_ids, 'wines_ids': wines_ids}), \
           200


@auto.doc()
@mod.route('/chef/id=<int:id>', methods=['GET'])
def get_chef_recipes(id):
    """
    Get information about all recipes for chef with special id.
    :param id: chef id
    :param offset (GET param) : starts from which recipes
    :param limit (GET param) : how many recipes you want to get
    :return: json with parameters:
            error_code - server response_code
            result - information about recipes
            entities_count - numbers of all chefs recipes
    """
    recipes = []
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', type=int)
    if current_user.is_authenticated() and current_user.role_code == 0:
        recipe_query = Recipe.query
    else:
        recipe_query = Recipe.query.filter_by(type=PUBLISHED)
    count = recipe_query.filter_by(chef_id=id).count()
    if limit is not None and offset is not None:
        recipes_band = recipe_query.filter_by(chef_id=id).slice(start=offset, stop=limit+offset).all()
    else:
        recipes_band = recipe_query.filter_by(chef_id=id)
    for recipe in recipes_band:
        information = recipe_response_builder(recipe)
        information['ingredients'] = get_ingredients_by_divisions(recipe.id)
        hash_of_information = make_hash(information)
        information['hash'] = hash_of_information
        recipes.append(information)
    return jsonify({'error_code': OK, 'result': recipes, 'entities_count': count}), 200


@auto.doc()
@mod.route('/category/id=<int:id>', methods=['GET'])
def get_category_recipes(id):
    """
    Get information about all recipes in category with special id.
    :param id: category id
    :param offset (GET param) : starts from which recipes
    :param limit (GET param) : how many recipes you want to get
    :return: json with parameters:
            error_code - server response_code
            result - information about recipes
            entities_count - numbers of all chefs recipes
    """
    recipes = []
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', type=int)
    if current_user.is_authenticated() and current_user.role_code == 0:
        recipe_query = Recipe.query
    else:
        recipe_query = Recipe.query.filter_by(type=PUBLISHED)
    count = recipe_query.join(Category.recipes).filter(Category.id == id).count()
    if limit is not None and offset is not None:
        recipes_band = recipe_query.join(Category.recipes).filter(Category.id == id).slice(start=offset, stop=limit+offset).all()
    else:
        recipes_band = recipe_query.join(Category.recipes).filter(Category.id == id).all()
    for recipe in recipes_band:
        information = recipe_response_builder(recipe)
        information['ingredients'] = get_ingredients_by_divisions(recipe.id)
        hash_of_information = make_hash(information)
        information['hash'] = hash_of_information
        recipes.append(information)
    return jsonify({'error_code': OK, 'result': recipes, 'entities_count': count}), 200


@auto.doc()
@mod.route('/set/id=<int:id>', methods=['GET'])
def get_set_recipes(id):
    """
    Get information about all recipes in set with special id.
    :param id: set id
    :param offset (GET param) : starts from which recipes
    :param limit (GET param) : how many recipes you want to get
    :return: json with parameters:
            error_code - server response_code
            result - information about recipes
            entities_count - numbers of all chefs recipes
    """
    recipes = []
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', type=int)
    if current_user.is_authenticated() and current_user.role_code == 0:
        recipe_query = Recipe.query
    else:
        recipe_query = Recipe.query.filter_by(type=PUBLISHED)
    count = recipe_query.join(Set.recipes).filter(Set.id == id).count()
    if limit is not None and offset is not None:
        recipes_band = recipe_query.join(Set.recipes).filter(Set.id == id).slice(start=offset, stop=limit+offset).all()
    else:
        recipes_band = recipe_query.join(Set.recipes).filter(Set.id == id).all()
    for recipe in recipes_band:
        information = recipe_response_builder(recipe)
        information['ingredients'] = get_ingredients_by_divisions(recipe.id)
        hash_of_information = make_hash(information)
        information['hash'] = hash_of_information
        recipes.append(information)
    return jsonify({'error_code': OK, 'result': recipes, 'entities_count': count}), 200


@auto.doc()
@mod.route('/feed', methods=['GET'])
def get_feed():
    """
    Get information about all exist recipes, sets and wines.
    :param page (GET param) : which page you want to get
    :return: json with parameters:
            error_code - server response_code
            result - information about objects
            is_last_page  - is current page last or not
            recipes_ids - ids of all recipes
            sets_ids - ids of all sets
            wines_ids - ids of all wines
    """
    recipes = []
    sets = []
    wines = []
    if current_user.is_authenticated() and current_user.role_code == 0:
        recipe_query = Recipe.query
    else:
        recipe_query = Recipe.query.filter_by(type=PUBLISHED)
    page = request.args.get('page', type=int)
    if page is not None:
        # for faster loading
        limit_recipes = 2
        offset_recipes = (page-1)*limit_recipes
        limit_sets = 1
        offset_sets = (page-1)*limit_recipes
        limit_wines = 2
        offset_wines = (page-1)*limit_recipes
        recipes_band = recipe_query.slice(start=offset_recipes, stop=limit_recipes+offset_recipes).all()
        sets_band = Set.query.slice(start=offset_sets, stop=limit_sets+offset_sets).all()
        wines_band = Wine.query.slice(start=offset_wines, stop=limit_wines+offset_wines).all()
        next_recipe = recipe_query.slice(start=limit_recipes+offset_recipes, stop=limit_recipes+offset_recipes+1).first()
        next_set = Set.query.slice(start=limit_sets+offset_sets, stop=limit_sets+offset_sets+1).first()
        next_wine = Wine.query.slice(start=limit_wines+offset_wines, stop=limit_wines+offset_wines+1).first()
        if next_recipe or next_set or next_wine:
            is_last_page = False
        else:
            is_last_page = True
    else:
        recipes_band = recipe_query.all()
        sets_band = Set.query.all()
        wines_band = Wine.query.all()
        is_last_page = True
    for recipe in recipes_band:
        information = recipe_response_builder(recipe)
        information['ingredients'] = get_ingredients_by_divisions(recipe.id)
        hash_of_information = make_hash(information)
        information['hash'] = hash_of_information
        information['type_of_object'] = 'recipe'
        recipes.append(information)
    recipes_ids = []
    recipes_all = recipe_query.all()
    for recipe in recipes_all:
        recipes_ids.append(recipe.id)
    for set in sets_band:
        information = set_response_builder(set)
        information['type_of_object'] = 'set'
        sets.append(information)
    sets_ids = []
    sets_all = Set.query.all()
    for set in sets_all:
        sets_ids.append(set.id)
    for wine in wines_band:
        information = wine_response_builder(wine)
        information['type_of_object'] = 'wine'
        wines.append(information)
    wines_ids = []
    wines_all = Wine.query.all()
    for wine in wines_all:
        wines_ids.append(wine.id)
    feed = recipes + sets + wines
    return jsonify({'error_code': OK, 'result': feed, 'is_last_page': is_last_page, 'recipes_ids': recipes_ids,
                    'sets_ids': sets_ids, 'wines_ids': wines_ids}), 200


@auto.doc()
@mod.route('/search', methods=['GET'])
def get_searched_goods_and_wines():
    """
    Get information about recipes and wines find by search.
    :param q (GET param) : searching query in title
    :param category (GET param) : searching recipes in which category
    :param type_of_grape (GET param) : searching wines with type_of_grape
    :param page (GET param) : which page you want to get
    :return: json with parameters:
            error_code - server response_code
            result - information about objects
            is_last_page  - is current page last or not
            recipes_ids - ids of all recipes
            wines_ids - ids of all wines
    """
    recipes = []
    wines = []
    q = request.args.get('q', type=unicode, default=u'')
    category = request.args.get('category', type=int)
    type_of_grape = request.args.get('type_of_grape', type=int)
    page = request.args.get('page', type=int)
    if current_user.is_authenticated() and current_user.role_code == 0:
        recipe_query = Recipe.query
    else:
        recipe_query = Recipe.query.filter_by(type=PUBLISHED)
    if category is not None:
        category = Category.query.filter_by(id=category).first()
        if category:
            recipes_band = recipe_query.filter(Recipe.categories.contains(category))
        else:
            recipes_band = recipe_query.filter(db.false())
    else:
        recipes_band = recipe_query
    if type_of_grape is not None:
        wines_band = Wine.query.filter_by(type_of_grape_id=type_of_grape)
    else:
        wines_band = Wine.query
    if page is not None:
        # for faster loading
        limit_recipes = 3
        offset_recipes = (page-1)*limit_recipes
        limit_wines = 3
        offset_wines = (page-1)*limit_recipes
        old_recipes_band = recipes_band
        old_wines_band = wines_band
        recipes_band = old_recipes_band\
                                   .filter(Recipe.title.ilike('%' + q + '%'))\
                                   .slice(start=offset_recipes, stop=limit_recipes+offset_recipes).all()
        wines_band = old_wines_band\
                               .filter(Wine.title.ilike('%' + q + '%'))\
                               .slice(start=offset_wines, stop=limit_wines+offset_wines).all()
        next_recipe = old_recipes_band\
                                  .filter(Recipe.title.ilike('%' + q + '%'))\
                                  .slice(start=limit_recipes+offset_recipes, stop=limit_recipes+offset_recipes+1).first()
        next_wine = old_wines_band\
                              .filter(Wine.title.ilike('%' + q + '%'))\
                              .slice(start=limit_wines+offset_wines, stop=limit_wines+offset_wines+1).first()
        if next_recipe or next_wine:
            is_last_page = False
        else:
            is_last_page = True
    else:
        recipes_band = recipes_band.filter(Recipe.title.ilike('%' + q + '%')).all()
        wines_band = wines_band.filter(Wine.title.ilike('%' + q + '%')).all()
        is_last_page = True
    for recipe in recipes_band:
        information = recipe_response_builder(recipe)
        information['ingredients'] = get_ingredients_by_divisions(recipe.id)
        hash_of_information = make_hash(information)
        information['hash'] = hash_of_information
        information['type_of_object'] = 'recipe'
        recipes.append(information)
    for wine in wines_band:
        information = wine_response_builder(wine)
        information['type_of_object'] = 'wine'
        wines.append(information)
    feed = recipes + wines
    return jsonify({'error_code': OK, 'result': feed, 'is_last_page': is_last_page}), 200


def recipe_response_builder(recipe, excluded=[]):
    categories = []
    if current_user.is_authenticated() and current_user.role_code == 0:
        recipe_query = Recipe.query
    else:
        recipe_query = Recipe.query.filter_by(type=PUBLISHED)
    for category in recipe_query.filter_by(id=recipe.id).first().categories:
        categories.append(category.id)
    cuisine_types = []
    for cuisine_type in recipe_query.filter_by(id=recipe.id).first().cuisine_types:
        cuisine_types.append(cuisine_type.id)
    tools = []
    for tool in recipe_query.filter_by(id=recipe.id).first().tools:
        tools.append(tool.id)
    wines = []
    for wine in recipe_query.filter_by(id=recipe.id).first().wines:
        wines.append(wine.id)
    information = response_builder(recipe, Recipe, excluded)
    information['categories'] = []
    if categories is not None:
        for category_id in categories:
            category = Category.query.get(category_id)
            category_information = response_builder(category, Category)
            information["categories"].append(category_information)
    information['cuisine_types'] = []
    if cuisine_types is not None:
        for cuisine_type_id in cuisine_types:
            cuisine_type = CuisineType.query.get(cuisine_type_id)
            cuisine_type_information = response_builder(cuisine_type, CuisineType)
            information["cuisine_types"].append(cuisine_type_information)
    information['tools'] = []
    if tools is not None:
        for tool_id in tools:
            tool = Tool.query.get(tool_id)
            tool_information = response_builder(tool, Tool)
            information["tools"].append(tool_information)
    information['wines'] = []
    if wines is not None:
        for wine_id in wines:
            wine = Wine.query.get(wine_id)
            wine_information = wine_response_builder(wine)
            information["wines"].append(wine_information)
    information['photos'] = []
    for photo in RecipePhoto.query.filter_by(item_id=recipe.id):
        photo_information = response_builder(photo, RecipePhoto)
        information['photos'].append(photo_information)
    information['ingredients'] = []
    for ingredient in Ingredient.query.filter_by(recipe_id=recipe.id):
        ingredient_information = response_builder(ingredient, Ingredient, excluded=["recipe_id"])
        information['ingredients'].append(ingredient_information)
    information['instructions'] = []
    for instruction in InstructionItem.query.filter_by(recipe_id=recipe.id):
        instruction_information = response_builder(instruction, InstructionItem, excluded=["recipe_id"])
        information['instructions'].append(instruction_information)
    information['likes'] = Like.query.filter_by(recipe_id=recipe.id).count()
    if not recipe.set_id:
        information['is_open'] = True
    elif not current_user.is_authenticated():
        information['is_open'] = False
    elif UserSet.query.filter_by(set_id=recipe.set_id, user_id=current_user.id).first():
        user_set = UserSet.query.filter_by(set_id=recipe.set_id, user_id=current_user.id).first()
        if user_set.open_type == FOREVER:
            information['is_open'] = True
        if user_set.open_type == MONTH:
            if (datetime.utcnow() - user_set.open_date).days <= 30:
                information['is_open'] = True
            else:
                information['is_open'] = False
    else:
        information['is_open'] = False
    return information


def set_response_builder(set, excluded=[]):
    information = response_builder(set, Set, excluded)
    information['number_of_recipes'] = len(set.recipes)
    if not current_user.is_authenticated():
        information['is_open'] = False
    else:
        user_set = UserSet.query.filter_by(set_id=set.id, user_id=current_user.id).first()
        if user_set:
            if user_set.open_type == FOREVER:
                information['is_open'] = True
            if user_set.open_type == MONTH:
                if (datetime.utcnow() - user_set.open_date).days <= 30:
                    information['is_open'] = True
                else:
                    information['is_open'] = False
        else:
            information['is_open'] = False
    return information