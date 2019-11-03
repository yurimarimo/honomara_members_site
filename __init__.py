from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://honomara:honomara@localhost/honomara'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.jinja_env.globals.update(len=len, int=int)

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from honomara_members_site import routes
from honomara_members_site import login
