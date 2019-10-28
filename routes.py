from flask import render_template, request, abort, redirect, url_for
from flask_bootstrap import Bootstrap
from honomara_members_site import app
from honomara_members_site.login import user_check, users
from honomara_members_site.model import Member
from flask_login import login_required, login_user, logout_user

bootstrap = Bootstrap(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login/', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        if(request.form["username"] in user_check and request.form["password"] == user_check[request.form["username"]]["password"]):
            login_user(users.get(user_check[request.form["username"]]["id"]))
            return redirect(url_for('index'))
        else:
            return abort(401)
    else:
        return render_template("login.html")


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/manage')
@login_required
def manage():
    return render_template('manage.html')


@app.route('/member')
@login_required
def member():
    members = Member.query.order_by(Member.year.desc())
    return render_template('member.html', members=members)
