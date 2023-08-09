from flask import Flask
from app.config import Db_config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.prefix_middleware import PrefixMiddleware

app = Flask(__name__)
app.config.from_object(Db_config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# URL prefix
app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/perpus-api/v1')

from app.models import user, roles
from app.models.roles import create_roles
from app.models.user import create_super_admin
create_roles()
create_super_admin()

from app import routes
if __name__ == "__main__":
    app.run()