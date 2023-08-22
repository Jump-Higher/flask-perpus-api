from flask import Flask
from config import Db_config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.prefix_middleware import PrefixMiddleware
from flask_jwt_extended import JWTManager
import os

app = Flask(__name__)
app.config.from_object(Db_config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Setup JWT Config
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

# URL prefix
app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/perpus-api/v1')

from app.models import roles, users, cart, authors, books, bookshelves, borrows, borrow_details, categories, publishers, returns, return_details

# Create Roles
from app.models.roles import create_roles
create_roles()

# Create Super Admin User
from app.models.users import create_super_admin
create_super_admin()

from app import routes
if __name__ == "__main__":
    app.run()