from flask import render_template, request, abort, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from honomara_members_site import app
from honomara_members_site.login import user_check, users
from honomara_members_site.model import db, Member, Training, After, Restaurant, Race
from flask_login import login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, IntegerField
from wtforms import HiddenField, TextAreaField, DateField, SelectMultipleField, SelectField
from wtforms.validators import Optional, InputRequired


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
    year = IntegerField('入学年度:', validators=[InputRequired()])
    family_name = StringField('姓:', validators=[InputRequired()])
    family_kana = StringField('カナ(姓):', validators=[InputRequired()])
    first_name = StringField('名:', validators=[InputRequired()])
    first_kana = StringField('カナ(名):', validators=[InputRequired()])
    show_name = StringField('表示名:', validators=[InputRequired()])
    sex = RadioField('性別:', default=0, coerce=int,
                     choices=[(0, '男'), (1, '女')])
    visible = RadioField('状態:', coerce=bool, choices=[
                         (True, '表示'), (False, '非表示')],
                         validators=[InputRequired()])
    method = HiddenField(validators=[Optional()])
    confirmed = HiddenField(validators=[Optional()])
    submit = SubmitField('確定')


@app.route('/member/edit', methods=['GET', 'POST'])
@login_required
def member_edit():
    form = MemberForm(formdata=request.form)
    form.visible.data = request.form.get('visible') != 'False'

    if form.validate_on_submit():
        return redirect(url_for('member_confirm'), code=307)

    if request.args.get('method') == 'PUT':
        member_id = int(request.args.get('member_id'))
        member = Member.query.get(member_id)
        form = MemberForm(obj=member)
        form.method.data = 'PUT'
    else:
        form.method.data = 'POST'
    return render_template('member_edit.html', form=form)


@app.route('/member/confirm', methods=['POST'])
@login_required
def member_confirm():
    form = MemberForm(formdata=request.form)
    form.visible.data = request.form.get('visible') != 'False'

    if request.form.get('submit') == 'キャンセル':
        return redirect(url_for('user'))

    if form.validate_on_submit() and request.form.get('confirmed'):
        if request.form.get('method') == 'DELETE':
            member = Member.query.get(form.member_id.data)
            db.session.delete(member)
        elif request.form.get('method') == 'PUT':
            member = Member.query.get(form.member_id.data)
            form.populate_obj(member)
        elif request.form.get('method') == 'POST':
            member = Member()
            form.populate_obj(member)
            member.member_id = None
            member.kana = member.family_kana + member.first_kana
            db.session.add(member)
        db.session.commit()
        return redirect(url_for('member'))
    else:
        if request.form.get('method') == 'DELETE':
            member = Member.query.get(form.member_id.data)
            form = MemberForm(obj=member)
        return render_template('member_confirm.html', form=form)


@app.route('/training/')
def training():
    per_page = 20
    page = request.args.get('page') or 1
    page = max([1, int(page)])
    trainings = Training.query.order_by(
        Training.date.desc()).paginate(page, per_page)
    return render_template('training.html', pagination=trainings)


q1 = Member.query.filter_by(visible=True, year=2019).all()
q2 = Member.query.filter_by(visible=True, year=2018).all()
q3 = Member.query.filter_by(visible=True, year=2017).all()
q4 = Member.query.filter_by(visible=True, year=2016).all()
q56 = Member.query.filter_by(visible=True, year=2015).all() + \
    Member.query.filter_by(visible=True, year=2014).all()
q7_ = Member.query.filter_by(visible=True).filter(
    Member.year < 2015).order_by(Member.year.desc()).all()

visible_member_list_for_form = [(m.member_id, m.show_name)
                                for m in (q1 + q2 + q3 + q4 + q56 + q7_)]


class TrainingForm(FlaskForm):
    training_id = HiddenField(validators=[Optional()])
    date = DateField('練習日:', validators=[InputRequired()])
    place = StringField('練習場所:', validators=[InputRequired()])
    weather = StringField('天気:', validators=[Optional()])
    participants = SelectMultipleField('参加者:', coerce=int, validators=[InputRequired()],
                                       choices=visible_member_list_for_form)
    title = StringField('タイトル:', validators=[InputRequired()])
    comment = TextAreaField('コメント:', validators=[Optional()])
    confirmed = HiddenField(validators=[Optional()])
    method = HiddenField(validators=[Optional()])
    submit = SubmitField('確定', validators=[Optional()])


@app.route('/training/edit', methods=['GET', 'POST'])
@login_required
def training_edit():
    form = TrainingForm(formdata=request.form)

    if form.validate_on_submit():
        return redirect(url_for('training_confirm'), code=307)

    if request.args.get('method') == 'PUT':
        training_id = int(request.args.get('training_id'))
        training = Training.query.get(training_id)
        form = TrainingForm(obj=training)
        form.method.data = 'PUT'
        form.participants.data = [m.member_id for m in training.participants]
    else:
        form.method.data = 'POST'

    return render_template('training_edit.html', form=form)


@app.route('/training/confirm', methods=['POST'])
@login_required
def training_confirm():
    form = TrainingForm(formdata=request.form)
    if request.form.get('submit') == 'キャンセル':
        return redirect(url_for('training'))

    if form.participants.data:
        form.participants.data = [Member.query.get(
            int(member_id)) for member_id in form.participants.data]

    if form.validate_on_submit() or request.form.get('confirmed'):
        if request.form.get('method') == 'DELETE':
            training = Training.query.get(form.training_id.data)
            db.session.delete(training)
        elif request.form.get('method') == 'PUT':
            training = Training.query.get(form.training_id.data)
            form.populate_obj(training)
        elif request.form.get('method') == 'POST':
            training = Training()
            form.populate_obj(training)
            training.training_id = None
            db.session.add(training)
        db.session.commit()
        return redirect(url_for('training'))
    else:
        if request.form.get('method') == 'DELETE':
            training = Training.query.get(form.training_id.data)
            form = TrainingForm(obj=training)
            form.participants.data = training.participants
        return render_template('training_confirm.html', form=form)


@app.route('/after/')
def after():
    per_page = 40
    page = request.args.get('page') or 1
    page = max([1, int(page)])
    afters = After.query.order_by(After.date.desc()).paginate(page, per_page)
    return render_template('after.html', pagination=afters)


restaurants_choices = [(r.restaurant_id, "{}({})".format(r.restaurant_name, r.place))
                       for r in Restaurant.query.all()]


class AfterForm(FlaskForm):
    after_id = HiddenField(validators=[Optional()])
    date = DateField('日付:', validators=[InputRequired()])
    after_stage = IntegerField('何次会:', validators=[InputRequired()])
    restaurant = SelectField('店:', coerce=int, validators=[InputRequired()],
                             choices=restaurants_choices)
    participants = SelectMultipleField('参加者:', coerce=int, validators=[InputRequired()],
                                       choices=visible_member_list_for_form
                                       )
    title = StringField('タイトル:', validators=[InputRequired()])
    comment = TextAreaField('コメント:', validators=[Optional()])
    confirmed = HiddenField(validators=[Optional()])
    method = HiddenField(validators=[Optional()])
    submit = SubmitField('確定', validators=[Optional()])


@app.route('/after/edit', methods=['GET', 'POST'])
@login_required
def after_edit():
    form = AfterForm(formdata=request.form)

    if form.validate_on_submit():
        return redirect(url_for('after_confirm'), code=307)

    if request.args.get('method') == 'PUT':
        after_id = int(request.args.get('after_id'))
        after = After.query.get(after_id)
        form = AfterForm(obj=after)
        form.participants.data = [m.member_id for m in after.participants]
        form.restaurant.data = after.restaurant.restaurant_id
        form.method.data = 'PUT'
    else:
        form.method.data = 'POST'

    return render_template('after_edit.html', form=form)


@app.route('/after/confirm', methods=['POST'])
@login_required
def after_confirm():
    form = AfterForm(formdata=request.form)
    app.logger.info(request.form)
    if request.form.get('submit') == 'キャンセル':
        return redirect(url_for('training'))

    if form.participants.data:
        form.participants.data = [Member.query.get(
            int(member_id)) for member_id in form.participants.data]

    if form.restaurant.data:
        form.restaurant.data = Restaurant.query.get(int(form.restaurant.data))

    app.logger.info(form.restaurant.data)
    if form.validate_on_submit() or request.form.get('confirmed'):
        if request.form.get('method') == 'DELETE':
            after = After.query.get(form.after_id.data)
            db.session.delete(after)
        elif request.form.get('method') == 'PUT':
            after = After.query.get(form.after_id.data)
            form.populate_obj(after)
        elif request.form.get('method') == 'POST':
            after = After()
            form.populate_obj(after)
            after.after_id = None
            db.session.add(after)
        db.session.commit()
        return redirect(url_for('after'))
    else:
        if request.form.get('method') == 'DELETE':
            after = After.query.get(form.after_id.data)
            form = AfterForm(obj=after)
            form.participants.data = after.participants
            form.restaurant.data = after.restaurant
        return render_template('after_confirm.html', form=form)


@app.route('/result/')
def result():
    per_page = 40
    page = request.args.get('page') or 1
    page = max([1, int(page)])
    results = Race.query.order_by(Race.date.desc()).paginate(page, per_page)
    return render_template('result.html', pagination=results)
