from flask import render_template, request, abort, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from honomara_members_site import app
from honomara_members_site.login import user_check, users
from honomara_members_site.model import db, Member
from flask_login import login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, IntegerField
from wtforms.validators import Required


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


@app.route('/manage/')
@login_required
def manage():
    return render_template('manage.html')


@app.route('/member/')
@login_required
def member():
    members = Member.query.order_by(Member.year.desc())
    return render_template('member.html', members=members)


class MemberForm(FlaskForm):
    year = IntegerField('入学年度:', validators=[Required()])
    family_name = StringField('姓:', validators=[Required()])
    family_kana = StringField('カナ(姓):', validators=[Required()])
    first_name = StringField('名:', validators=[Required()])
    first_kana = StringField('カナ(名):', validators=[Required()])
    show_name = StringField('表示名:', validators=[Required()])
    sex = RadioField('性別:', coerce=int, choices=[(0, '男'), (1, '女')])
    visible = RadioField('状態:', coerce=bool, choices=[(True, '表示'), (False, '非表示')])
    submit = SubmitField('登録')


@app.route('/member/edit', methods=['GET', 'POST'])
@login_required
def member_edit():
    form = MemberForm()
    app.logger.info(form.validate_on_submit())

    if form.validate_on_submit():
        return redirect(url_for('member_confirm'), code=307)
    return render_template('member_edit.html', form=form)


@app.route('/member/confirm', methods=['POST'])
@login_required
def member_confirm():
    form = MemberForm()
    member = Member()
    form.populate_obj(member)
    if member.kana is None:
        member.kana = member.family_kana + member.first_kana

    if request.form.get('confirmed'):
        db.session.add(member)
        db.session.commit()
        flash('new member has been created!', 'success')
        return redirect(url_for('member'))
    return render_template('member_confirm.html', form=form)
