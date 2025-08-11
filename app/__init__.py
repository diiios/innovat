from flask import Flask
from .extentions import db
from .config import Config

from .routes.ideas import idea
from .routes.tools import tool
from .routes.resources import resources 
from .routes.events import event

from .routes.main import main
from .routes.test import test
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

def create_app():
    app = Flask(__name__)

    app.config.from_object('app.config.Config')

    app.register_blueprint(main)
    app.register_blueprint(idea, url_prefix='/ideas')
    app.register_blueprint(tool, url_prefix='/tools')
    
    app.register_blueprint(resources, url_prefix='/resources')
    app.register_blueprint(event, url_prefix='/events')

    app.register_blueprint(test, url_prefix='/test')

    
    app.secret_key = '123'

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app