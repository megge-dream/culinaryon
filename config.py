import os
from app.utils import INSTANCE_FOLDER_PATH, make_dir

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

ADMINS = frozenset(['ff.warprobot@gmail.com'])
SECRET_KEY = 'This string will be replaced with a proper key in production.'
#SERVER_NAME = '127.0.0.1:5000'

SQLALCHEMY_DATABASE_URI = 'sqlite:////Users/megge/Documents/culinaryon/instance/app.sqlite'
SQLALCHEMY_ECHO = True
DATABASE_CONNECT_OPTIONS = {}

# FLASK LOGIN SETTINGS
REMEMBER_COOKIE_NAME = 'access_token'
SESSION_PROTECTION = None
#SECURITY_RESET_URL = '/reset'
SECURITY_RECOVERABLE = True


#THREADS_PER_PAGE = 8  # need more tests
# JSON_SORT_KEYS = False

# Uploading
UPLOAD_FOLDER = os.path.join(_basedir, 'uploads')
RECIPES_UPLOAD = os.path.join(UPLOAD_FOLDER, 'recipes')
CHEFS_UPLOAD = os.path.join(UPLOAD_FOLDER, 'chefs')
SCHOOLS_UPLOAD = os.path.join(UPLOAD_FOLDER, 'schools')
TOOLS_UPLOAD = os.path.join(UPLOAD_FOLDER, 'tools')
SCHOOL_ITEMS_UPLOAD = os.path.join(UPLOAD_FOLDER, 'school_items')
INSTRUCTION_ITEMS_UPLOAD = os.path.join(UPLOAD_FOLDER, 'instruction_items')
CATEGORY_UPLOAD = os.path.join(UPLOAD_FOLDER, 'categories')
SET_UPLOAD = os.path.join(UPLOAD_FOLDER, 'sets')
WINE_UPLOAD = os.path.join(UPLOAD_FOLDER, 'wines')
TYPE_OF_GRAPE_UPLOAD = os.path.join(UPLOAD_FOLDER, 'type_of_grapes')

# create folders if not exist
make_dir(UPLOAD_FOLDER)
make_dir(RECIPES_UPLOAD)
make_dir(CHEFS_UPLOAD)
make_dir(SCHOOLS_UPLOAD)
make_dir(TOOLS_UPLOAD)
make_dir(CHEFS_UPLOAD)
make_dir(SCHOOL_ITEMS_UPLOAD)
make_dir(INSTRUCTION_ITEMS_UPLOAD)
make_dir(CATEGORY_UPLOAD)
make_dir(SET_UPLOAD)
make_dir(WINE_UPLOAD)
make_dir(TYPE_OF_GRAPE_UPLOAD)
# Dont forget to set to True in production
WTF_CSRF_ENABLED = False

MAIL_SERVER = 'mail.nic.ru'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'app@culinaryon.com'
MAIL_PASSWORD = '34thEHLHyc2WU'

