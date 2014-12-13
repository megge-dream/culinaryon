import app
from app.api.chefs.model import Chef
from app.api.recipes.model import Recipe
from app.api.schools.model import School
from app.api.users.model import User


def response_builder(current_object, entity, excluded=[]):
    """
    Helps to build appropriate response, parsing given object and included/excluded needed fields
    :param current_object: current object, from which we want to build a response
    :param entity: global entity the given object belongs to.
    :param excluded: array of fields we do not want to see in response.
    :return: return a dict with needed fields
    """
    result = {}
    print(current_object)
    excluded.append('is_deleted')
    print(current_object)
    for columnName in entity.__table__.columns.keys():
        print(current_object)
        print(columnName)
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
                result[columnName] = getattr(current_object, columnName)
    return result


def allowed_file(filename):
    """
    Check if loaded file match the cases.
    :param filename: the full file name with '.*' extension
    :return: True if matches or not
    """
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']
