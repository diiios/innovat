import os

class Config(object):
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:innovat.db'
    SQLALCHEMY_DATABASE_URI = 'postgresql://innovatsql_user:1x6sYfRAraHJTz1ScpOSkAY3je6nRhFq@dpg-d2d5k11r0fns73ai5i20-a.frankfurt-postgres.render.com/innovatsql'    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_IDEA_PHOTOS = 'app/static/uploads/ideas/photos'
    UPLOAD_IDEA_FILES = 'app/static/uploads/ideas/files'


    UPLOAD_RES = 'static/uploads/resources'

    UPLOAD_TOOL_ROOT = 'app/static/uploads/tools'
