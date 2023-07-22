from flask import Flask
from flask_cors import CORS
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    cache.init_app(app)
    
    from .main import main
    app.register_blueprint(main, url_prefix="/")
    
    return app