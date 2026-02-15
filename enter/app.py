from enter.extensions import db, login_manager
from flask import Flask
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

app =Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']=f'mysql+pymysql://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}:3306/{config.DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']='your_secret_key'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024
db.init_app(app)
login_manager.init_app(app)

from routes.user_routes import user_bp
from routes.admin_routes import admin_bp

app.register_blueprint(user_bp,url_prefix='/user')
app.register_blueprint(admin_bp,url_prefix='/')

with app.app_context():
    db.create_all()

