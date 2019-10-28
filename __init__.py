from flask import Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://honomara:honomara@localhost/honomara'
app.jinja_env.globals.update(len=len)

from honomara_members_site import login
from honomara_members_site import routes
