from flask import render_template
from flask_bootstrap import Bootstrap
from honomara_members_site import app

bootstrap = Bootstrap(app)


@app.route('/')
def index():
    return render_template('index.html')
    