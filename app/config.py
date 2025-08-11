import os

class Config(object):
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:innovat.db'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1386@localhost:5432/innovat'    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_IDEA_PHOTOS = 'app/static/uploads/ideas/photos'
    UPLOAD_IDEA_FILES = 'app/static/uploads/ideas/files'


    UPLOAD_RES = 'static/uploads/resources'

    UPLOAD_TOOL_ROOT = 'app/static/uploads/tools'