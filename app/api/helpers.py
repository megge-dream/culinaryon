# import app
# encoding: utf-8
import copy
import string
import random
from flask.ext.login import current_user, AnonymousUserMixin
from app.api import app, Ingredient, Basket, Category, Wine, Set, TypeOfGrape
from app.api.chefs.model import Chef
from app.api.recipes.model import Recipe, InstructionItem
from app.api.schools.model import School, SchoolItem
from app.api.users.constants import PUBLISHED
from app.api.users.model import User
from app.api.tools.model import Tool
from app.api.photos.model import *


def response_builder(current_object, entity, lang=u'en', excluded=[]):
    """
    Helps to build appropriate response, parsing given object and included/excluded needed fields
    :param current_object: current object, from which we want to build a response
    :param entity: global entity the given object belongs to.
    :param lang: language for result.
    :param excluded: array of fields we do not want to see in response.
    :return: return a dict with needed fields
    """
    result = {}
    current_lang = u'lang_' + lang
    excluded.append('is_deleted')
    for columnName in entity.__table__.columns.keys():
        if columnName not in excluded and ('lang' not in columnName or current_lang in columnName):
            if entity == Ingredient:
                if current_user.is_authenticated() and Basket.query.filter_by(user_id=current_user.id,
                                                                              ingredient_id=current_object.id).all():
                        result['is_in_basket'] = True
                else:
                    result['is_in_basket'] = False
            if "amount_of_persons" == columnName and (getattr(current_object, columnName) is None
                                                      or getattr(current_object, columnName) is None):
                result[columnName] = 0
            elif "complexity" == columnName:
                result[columnName] = getattr(current_object, columnName) if getattr(current_object,
                                                                                    columnName) is not None else 0
            elif "recipe" in columnName:
                recipe_id = getattr(current_object, columnName)
                if recipe_id is not None:
                    if current_user.is_authenticated() and current_user.role_code == 0:
                        recipe_query = Recipe.query
                    else:
                        recipe_query = Recipe.query.filter_by(type=PUBLISHED)
                    result["recipe"] = response_builder(recipe_query.get(recipe_id), Recipe, lang=lang)
            elif "chef" in columnName:
                chef_id = getattr(current_object, columnName)
                result["chef"] = chef_id
                if chef_id is not None and entity != Recipe:
                    result["chef"] = response_builder(Chef.query.get(chef_id), Chef, lang=lang)
            elif "school" in columnName:
                school_id = getattr(current_object, columnName)
                if school_id is not None:
                    result["school"] = response_builder(School.query.get(school_id), School, lang=lang)
            elif "type_of_grape" in columnName:
                type_of_grape_id = getattr(current_object, columnName)
                if type_of_grape_id is not None:
                    result["type_of_grape"] = response_builder(TypeOfGrape.query.get(type_of_grape_id), TypeOfGrape, lang=lang)
                else:
                    result["type_of_grape"] = []
            elif "user" in columnName and columnName != "provider_user_id":
                user_id = getattr(current_object, columnName)
                if user_id is not None:
                    if columnName == "user_id":
                        columnName = "user"
                    result[columnName] = response_builder(User.query.get(user_id), User, lang=lang, excluded=["password"])
            else:
                if 'photo' in columnName and getattr(current_object, columnName) is not None:
                    if entity is Recipe or entity is RecipePhoto:
                        result[columnName] = url_for('static', _scheme='http', _external=True,
                                                     filename='recipes/' + str(getattr(current_object, columnName)))
                    elif entity is Chef or entity is ChefPhoto:
                        result[columnName] = url_for('static', _scheme='http', _external=True,
                                                     filename='chefs/' + str(getattr(current_object, columnName)))
                    elif entity is School or entity is SchoolPhoto:
                        result[columnName] = url_for('static', _scheme='http', _external=True,
                                                     filename='schools/' + str(getattr(current_object, columnName)))
                    elif entity is Tool:
                        result[columnName] = url_for('static', _scheme='http', _external=True,
                                                     filename='tools/' + str(getattr(current_object, columnName)))
                    elif entity is SchoolItem:
                        result[columnName] = url_for('static', _scheme='http', _external=True,
                                                     filename='school_items/' + str(
                                                         getattr(current_object, columnName)))
                    elif entity is InstructionItem:
                        result[columnName] = url_for('static', _scheme='http', _external=True,
                                                     filename='instruction_items/' + str(
                                                         getattr(current_object, columnName)))
                    elif entity is Category:
                        result[columnName] = url_for('static', _scheme='http', _external=True,
                                                     filename='categories/' + str(
                                                         getattr(current_object, columnName)))
                    elif entity is Wine:
                        result[columnName] = url_for('static', _scheme='http', _external=True,
                                                     filename='wines/' + str(
                                                         getattr(current_object, columnName)))
                    elif entity is Set:
                        result[columnName] = url_for('static', _scheme='http', _external=True,
                                                     filename='sets/' + str(
                                                         getattr(current_object, columnName)))
                    else:
                        result[columnName] = url_for('static', _scheme='http', _external=True,
                                                     filename='' + str(getattr(current_object, columnName)))
                else:
                    if columnName == "id" and entity == User:
                        result["user_id"] = getattr(current_object, columnName) if getattr(current_object,
                                                                                        columnName) is not None else ''
                    elif entity == Ingredient and "title" in columnName and \
                            getattr(current_object, columnName) and ":" in getattr(current_object, columnName):
                        if "lang" in columnName:
                            result[columnName.rsplit('_', 2)[0]] = getattr(current_object, columnName).split(':')[1][1:]
                        else:
                            result[columnName] = getattr(current_object, columnName).split(':')[1][1:]
                    elif "lang" in columnName:
                        result[columnName.rsplit('_', 2)[0]] = getattr(current_object, columnName) if getattr(current_object,
                                                                                                columnName) is not None else ''
                    else:
                        result[columnName] = getattr(current_object, columnName) if getattr(current_object,
                                                                                        columnName) is not None else ''
    return result


def allowed_file(filename):
    """
    Check if loaded file match the cases.
    :param filename: the full file name with '.*' extension
    :return: True if matches or not
    """
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


DictProxyType = type(object.__dict__)


def make_hash(o):
    """
    Makes a hash from a dictionary, list, tuple or set to any level, that
    contains only other hashable types (including any lists, tuples, sets, and
    dictionaries). In the case where other kinds of objects (like classes) need
    to be hashed, pass in a collection of object attributes that are pertinent.
    For example, a class can be hashed in this fashion:

    make_hash([cls.__dict__, cls.__name__])

    A function can be hashed like so:

    make_hash([fn.__dict__, fn.__code__])
    """
    if type(o) == DictProxyType:
        o2 = {}
        for k, v in o.items():
            if not k.startswith("__"):
                o2[k] = v
        o = o2
    if isinstance(o, (set, tuple, list)):
        return tuple([make_hash(e) for e in o])
    elif not isinstance(o, dict):
        return hash(o)
    new_o = copy.deepcopy(o)
    for k, v in new_o.items():
        new_o[k] = make_hash(v)
    return hash(tuple(frozenset(sorted(new_o.items()))))


def get_ingredients_by_divisions(recipe_id, lang=u'en'):
    ingredients = []
    division = []
    division_names = []
    for ingredient in Ingredient.query.filter_by(recipe_id=recipe_id):
        information = response_builder(ingredient, Ingredient, lang=lang, excluded=["recipe_id"])
        if lang == 'en':
            if ingredient.title_lang_en and ":" in ingredient.title_lang_en:
                division_info = {}
                division_name = ingredient.title_lang_en.split(':')[0]
                if division_name in division_names:
                    for d in division:
                        if d['name'] == division_name:
                            d['ingredients'].append(information)
                else:
                    division_names.append(division_name)
                    division_info['ingredients'] = []
                    division_info['ingredients'].append(information)
                    division_info['name'] = division_name
                    division.append(division_info)
            else:
                ingredients.append(information)
        elif ingredient.title_lang_ru and lang == 'ru':
            if ":" in ingredient.title_lang_ru:
                division_info = {}
                division_name = ingredient.title_lang_ru.split(':')[0]
                if division_name in division_names:
                    for d in division:
                        if d['name'] == division_name:
                            d['ingredients'].append(information)
                else:
                    division_names.append(division_name)
                    division_info['ingredients'] = []
                    division_info['ingredients'].append(information)
                    division_info['name'] = division_name
                    division.append(division_info)
            else:
                ingredients.append(information)
    for d in division:
        ingredients.append(d)
    return ingredients


def code_generator(size=4, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))