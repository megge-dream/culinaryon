import os
from app.utils import INSTANCE_FOLDER_PATH, make_dir

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

ADMINS = frozenset(['ff.warprobot@gmail.com'])
SECRET_KEY = 'This string will be replaced with a proper key in production.'
SERVER_NAME = '127.0.0.1:5000'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')
SQLALCHEMY_ECHO = True
DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 8  # need more tests
# JSON_SORT_KEYS = False

# Uploading

UPLOAD_FOLDER = os.path.join(_basedir, 'uploads')
RECIPES_UPLOAD = os.path.join(UPLOAD_FOLDER, 'recipes')
CHEFS_UPLOAD = os.path.join(UPLOAD_FOLDER, 'chefs')
SCHOOLS_UPLOAD = os.path.join(UPLOAD_FOLDER, 'schools')
TOOLS_UPLOAD = os.path.join(UPLOAD_FOLDER, 'tools')
CHEFS_UPLOAD = os.path.join(UPLOAD_FOLDER, 'chefs')
SCHOOL_ITEMS_UPLOAD = os.path.join(UPLOAD_FOLDER, 'school_items')
INSTRUCTION_ITEMS_UPLOAD = os.path.join(UPLOAD_FOLDER, 'instruction_items')

# create folders if not exist
make_dir(UPLOAD_FOLDER)
make_dir(RECIPES_UPLOAD)
make_dir(CHEFS_UPLOAD)
make_dir(SCHOOLS_UPLOAD)
make_dir(TOOLS_UPLOAD)
make_dir(CHEFS_UPLOAD)
make_dir(SCHOOL_ITEMS_UPLOAD)
make_dir(INSTRUCTION_ITEMS_UPLOAD)
# Dont forget to set to True in production
WTF_CSRF_ENABLED = False

