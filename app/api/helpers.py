# import app
import copy
from app.api import app
from app.api.chefs.model import Chef
from app.api.recipes.model import Recipe, InstructionItem
from app.api.schools.model import School, SchoolItem
from app.api.users.model import User
from app.api.tools.model import Tool
from app.api.photos.model import *


def response_builder(current_object, entity, excluded=[]):
    """
    Helps to build appropriate response, parsing given object and included/excluded needed fields
    :param current_object: current object, from which we want to build a response
    :param entity: global entity the given object belongs to.
    :param excluded: array of fields we do not want to see in response.
    :return: return a dict with needed fields
    """
    result = {}
    excluded.append('is_deleted')
    for columnName in entity.__table__.columns.keys():
        if columnName not in excluded:
            if "recipe" in columnName:
                recipe_id = getattr(current_object, columnName)
                if recipe_id is not None:
                    result["recipe"] = response_builder(Recipe.query.get(recipe_id), Recipe)
            elif "chef" in columnName:
                chef_id = getattr(current_object, columnName)
                if chef_id is not None:
                    result["chef"] = response_builder(Chef.query.get(chef_id), Chef)
            elif "school" in columnName:
                school_id = getattr(current_object, columnName)
                if school_id is not None:
                    result["school"] = response_builder(School.query.get(school_id), School)
            elif "user" in columnName and columnName != "provider_user_id":
                user_id = getattr(current_object, columnName)
                if user_id is not None:
                    if columnName == "user_id":
                        columnName = "user"
                    result[columnName] = response_builder(User.query.get(user_id), User, ["password"])
            else:
                if 'photo' in columnName and getattr(current_object, columnName) is not None:
                    if entity is Recipe or entity is RecipePhoto:
                        result[columnName] = url_for('static', _scheme='http', _external=True, filename='recipes/' + str(getattr(current_object, columnName)))
                    elif entity is Chef or entity is ChefPhoto:
                        result[columnName] = url_for('static', _scheme='http', _external=True, filename='chefs/' + str(getattr(current_object, columnName)))
                    elif entity is School or entity is SchoolPhoto:
                        result[columnName] = url_for('static', _scheme='http', _external=True, filename='schools/' + str(getattr(current_object, columnName)))
                    elif entity is Tool:
                        result[columnName] = url_for('static', _scheme='http', _external=True, filename='tools/' + str(getattr(current_object, columnName)))
                    elif entity is SchoolItem:
                        result[columnName] = url_for('static', _scheme='http', _external=True, filename='school_items/' + str(getattr(current_object, columnName)))
                    elif entity is InstructionItem:
                        result[columnName] = url_for('static', _scheme='http', _external=True, filename='instruction_items/' + str(getattr(current_object, columnName)))
                    else:
                        result[columnName] = url_for('static', _scheme='http', _external=True, filename='/' + str(getattr(current_object, columnName)))
                else:
                    result[columnName] = getattr(current_object, columnName, default='')
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
