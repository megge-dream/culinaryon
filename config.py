import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

ADMINS = frozenset(['ff.warprobot@gmail.com'])
SECRET_KEY = 'This string will be replaced with a proper key in production.'
SERVER_NAME = '127.0.0.1:6000'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')
SQLALCHEMY_ECHO = True
DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 8  # need more tests
# JSON_SORT_KEYS = False

# Uploading
UPLOAD_FOLDER = '/app/static/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB  raise RequestEntityTooLarge