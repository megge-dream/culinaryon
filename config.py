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
make_dir(UPLOAD_FOLDER)
# Dont forget to set to True in production
WTF_CSRF_ENABLED = False

