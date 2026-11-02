from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
bcrypt = Bcrypt()
migrate = Migrate()
