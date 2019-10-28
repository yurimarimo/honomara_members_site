from flask import Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

from honomara_members_site import login
from honomara_members_site import routes
