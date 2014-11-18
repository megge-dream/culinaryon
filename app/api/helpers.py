import app
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
    excluded.append('is_deleted')
    for columnName in entity.__table__.columns.keys():
        if columnName not in excluded:
            if "user" in columnName:
                user_id = getattr(current_object, columnName)
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
