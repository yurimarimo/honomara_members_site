from flask import render_template, request, abort, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from honomara_members_site import app
from honomara_members_site.login import user_check, users
from honomara_members_site.model import db, Member, Training, After
from flask_login import login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, IntegerField, HiddenField
from wtforms.validators import Required, Optional


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
    member_id = HiddenField(validators=[Optional()])
    year = IntegerField('入学年度:', validators=[Required()])
    family_name = StringField('姓:', validators=[Required()])
    family_kana = StringField('カナ(姓):', validators=[Required()])
    first_name = StringField('名:', validators=[Required()])
    first_kana = StringField('カナ(名):', validators=[Required()])
    show_name = StringField('表示名:', validators=[Required()])
    sex = RadioField('性別:', default=0, coerce=int, choices=[(0, '男'), (1, '女')])
    visible = RadioField('状態:', coerce=bool, choices=[(True, '表示'), (False, '非表示')])
    _method = HiddenField(validators=[Optional()])
    submit = SubmitField('確定')


@app.route('/member/edit', methods=['GET', 'POST'])
@login_required
def member_edit():
    form = MemberForm()
    form.visible.data = request.form.get('visible') == 'True'

    if form.validate_on_submit():
        return redirect(url_for('member_confirm'), code=307)

    if request.args.get('_method') == 'PUT':
        app.logger.info('!!!!!!!!!!!!UPDATE!!!!!!!!!!!!!!')
        member_id = int(request.args.get('member_id'))
        member = Member.query.get(member_id)
        app.logger.info(member)
        form = MemberForm(obj=member)
        form.member_id.data = member_id
        app.logger.info(form)
        method = 'PUT'
    else:
        method = 'POST'
        app.logger.info('!!!!!!!!!!!!CREATE!!!!!!!!!!!!!!')

    return render_template('member_edit.html', form=form, method=method)


@app.route('/member/confirm', methods=['POST', 'PUT', 'DELETE'])
@login_required
def member_confirm():
    form = MemberForm()
    app.logger.info(request)
    app.logger.info(request.form)
    form.visible.data = request.form.get('visible') == 'True'

    if request.form.get('submit') == 'キャンセル':
        return redirect(url_for('user'))

    if request.form.get('confirmed'):
        app.logger.info(request.form)
        if request.form.get('_method') == 'DELETE':
            member = Member.query.get(form.member_id.data)
            db.session.delete(member)
            flash('member has been deleted!', 'success')
            db.session.commit()

        elif request.form.get('_method') == 'PUT':
            member = Member.query.get(form.member_id.data)
            form.populate_obj(member)
            db.session.commit()
        else:# POST
            member = Member()
            form.populate_obj(member)
            member.member_id = None
            if member.kana is None:
                member.kana = member.family_kana + member.first_kana
            db.session.add(member)
            flash('new member has been created!', 'success')
            db.session.commit()
        return redirect(url_for('member'))
    else:
        if request.form.get('_method') == 'DELETE':
            app.logger.info(form.member_id)
            member = Member.query.get(form.member_id.data)
            app.logger.info(member)
            form = MemberForm(obj=member)
            app.logger.info(form)
            method = 'DELETE'
        elif request.form.get('_method') == 'PUT':
            method = 'PUT'
        else:
            method = 'POST'

    return render_template('member_confirm.html', form=form, method=method)


@app.route('/training/')
def training():
    per_page = 20
    page = request.args.get('page') or 1
    page = max([1, int(page)])
    trainings = Training.query.order_by(Training.date.desc()).paginate(page, per_page)
    return render_template('training.html', pagination=trainings)


@app.route('/after/')
def after():
    per_page = 40
    page = request.args.get('page') or 1
    page = max([1, int(page)])
    afters = After.query.order_by(After.date.desc()).paginate(page, per_page)
    return render_template('after.html', pagination=afters)
