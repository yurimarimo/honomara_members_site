from flask import render_template, request, abort, redirect, url_for
from honomara_members_site import app, db, bootstrap
from honomara_members_site.login import user_check, users
from honomara_members_site.model import Member, Training, After, Restaurant, Race, RaceBase, RaceType, Result
from flask_login import login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, IntegerField, FloatField
from wtforms import HiddenField, TextAreaField, DateField, SelectMultipleField, SelectField
from wtforms.validators import Optional, InputRequired


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
    id = HiddenField(validators=[Optional()])
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
        id = int(request.args.get('id'))
        member = Member.query.get(id)
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
            member = Member.query.get(form.id.data)
            db.session.delete(member)
        elif request.form.get('method') == 'PUT':
            member = Member.query.get(form.id.data)
            form.populate_obj(member)
        elif request.form.get('method') == 'POST':
            member = Member()
            form.populate_obj(member)
            member.id = None
            member.kana = member.family_kana + member.first_kana
            db.session.add(member)
        db.session.commit()
        return redirect(url_for('member'))
    else:
        if request.form.get('method') == 'DELETE':
            member = Member.query.get(form.id.data)
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

visible_member_list_for_form = [(m.id, m.show_name)
                                for m in (q1 + q2 + q3 + q4 + q56 + q7_)]
# visible_member_list_for_form = []


class TrainingForm(FlaskForm):
    id = HiddenField(validators=[Optional()])
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
        id = int(request.args.get('id'))
        training = Training.query.get(id)
        form = TrainingForm(obj=training)
        form.method.data = 'PUT'
        form.participants.data = [m.id for m in training.participants]
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
            training = Training.query.get(form.id.data)
            db.session.delete(training)
        elif request.form.get('method') == 'PUT':
            training = Training.query.get(form.id.data)
            form.populate_obj(training)
        elif request.form.get('method') == 'POST':
            training = Training()
            form.populate_obj(training)
            training.id = None
            db.session.add(training)
        db.session.commit()
        return redirect(url_for('training'))
    else:
        if request.form.get('method') == 'DELETE':
            training = Training.query.get(form.id.data)
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


restaurants_choices = [(r.id, "{}({})".format(
    r.restaurant_name, r.place)) for r in Restaurant.query.all()]
# restaurants_choices = []


class AfterForm(FlaskForm):
    id = HiddenField(validators=[Optional()])
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
        id = int(request.args.get('id'))
        after = After.query.get(id)
        form = AfterForm(obj=after)
        form.participants.data = [m.id for m in after.participants]
        form.restaurant.data = after.restaurant.id
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
            after = After.query.get(form.id.data)
            db.session.delete(after)
        elif request.form.get('method') == 'PUT':
            after = After.query.get(form.id.data)
            form.populate_obj(after)
        elif request.form.get('method') == 'POST':
            after = After()
            form.populate_obj(after)
            after.id = None
            db.session.add(after)
        db.session.commit()
        return redirect(url_for('after'))
    else:
        if request.form.get('method') == 'DELETE':
            after = After.query.get(form.id.data)
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


@app.route('/race/')
def race():
    return redirect(url_for('result'))


race_base_list_for_form = [(r.race_name, r.race_name)
                           for r in RaceBase.query.all()]
# race_base_list_for_form = []


class RaceForm(FlaskForm):
    id = HiddenField(validators=[Optional()])
    race_name = SelectField('大会名:', coerce=str, validators=[Optional()],
                            choices=race_base_list_for_form)
    race_name_option = StringField('大会名（選択肢にない場合）:', validators=[Optional()])
    date = DateField('大会日時:', validators=[InputRequired()])
    comment = TextAreaField('コメント:', validators=[Optional()])
    confirmed = HiddenField(validators=[Optional()])
    method = HiddenField(validators=[Optional()])
    submit = SubmitField('確定', validators=[Optional()])


@app.route('/race/edit', methods=['GET', 'POST'])
@login_required
def race_edit():
    app.logger.info(request.form)
    RaceBaseForm.race_name.choices = [
        (r.race_name, r.race_name) for r in RaceBase.query.all()]
    form = RaceForm(formdata=request.form)

    if form.validate_on_submit():
        return redirect(url_for('race_confirm'), code=307)
    form.race_name.choices = [
        (r.race_name, r.race_name) for r in RaceBase.query.all()]

    if request.args.get('method') == 'PUT':
        id = int(request.args.get('id'))
        race = Race.query.get(id)
        form = RaceForm(obj=race)
        form.method.data = 'PUT'
    else:
        form.method.data = 'POST'

    return render_template('race_edit.html', form=form)


@app.route('/race/confirm', methods=['POST'])
@login_required
def race_confirm():
    form = RaceForm(formdata=request.form)
    # form.visible.data = request.form.get('visible') != 'False'
    app.logger.info(request.form)

    if request.form.get('submit') == 'キャンセル':
        return redirect(url_for('user'))

    if form.validate_on_submit() and request.form.get('confirmed'):
        if request.form.get('method') in ['PUT', 'POST'] and len(form.race_name_option.data) > 3:
            rb = RaceBase.query.get(form.race_name_option.data)
            if rb is None:
                rb = RaceBase()
                rb.race_name = form.race_name_option.data
                db.session.add(rb)
                db.session.commit()
                app.logger.info('register race_base {}'.format(rb))
            form.race_name.data = rb.race_name

        if request.form.get('method') == 'DELETE':
            race = Race.query.get(form.id.data)
            db.session.delete(race)
        elif request.form.get('method') == 'PUT':
            race = Race.query.get(form.id.data)
            form.populate_obj(race)
        elif request.form.get('method') == 'POST':
            race = Race()
            form.populate_obj(race)
            race.id = None
            db.session.add(race)
        db.session.commit()
        return redirect(url_for('race'))
    else:
        if request.form.get('method') == 'DELETE':
            race = Race.query.get(form.id.data)
            form = RaceForm(obj=race)
        return render_template('race_confirm.html', form=form)


class RaceBaseForm(FlaskForm):
    race_name = SelectField('大会名:', coerce=str, validators=[Optional()],
                            choices=race_base_list_for_form)
    race_name_option = StringField('大会名（選択肢にない場合）:', validators=[Optional()])
    prefecture = SelectField('開催都道府県:', validators=[InputRequired()],
                             choices=[('北海道', '北海道'), ('青森県', '青森県'), ('岩手県', '岩手県'),
                                      ('宮城県', '宮城県'), ('秋田県', '秋田県'),
                                      ('山形県', '山形県'), ('福島県', '福島県'),
                                      ('茨城県', '茨城県'), ('栃木県', '栃木県'),
                                      ('群馬県', '群馬県'), ('埼玉県', '埼玉県'),
                                      ('千葉県', '千葉県'), ('東京都', '東京都'),
                                      ('神奈川県', '神奈川県'), ('新潟県', '新潟県'),
                                      ('富山県', '富山県'), ('石川県', '石川県'),
                                      ('福井県', '福井県'), ('山梨県', '山梨県'), ('長野', '長野'),
                                      ('奈良県', '奈良県'), ('和歌山県', '和歌山県'),
                                      ('鳥取県', '鳥取県'), ('島根県', '島根県'),
                                      ('岡山県', '岡山県'), ('広島県', '広島県'),
                                      ('山口県', '山口県'),
                                      ('徳島県', '徳島県'),
                                      ('香川県', '香川県'), ('愛媛県',
                                                       '愛媛県'),
                                      ('高知県', '高知県'),
                                      ('福岡県', '福岡県'), ('佐賀県', '佐賀県'),
                                      ('長崎県', '長崎県'), ('熊本県',
                                                       '熊本県'), ('大分県', '大分県'),
                                      ('宮崎県', '宮崎県'), ('鹿児島県', '鹿児島県'),
                                      ('沖縄県', '沖縄県')])
    comment = TextAreaField('コメント:', validators=[Optional()])
    confirmed = HiddenField(validators=[Optional()])
    method = HiddenField(validators=[Optional()])
    submit = SubmitField('確定', validators=[Optional()])


race_list_for_form = [(r.id, r.race_name) for r in Race.query.all()]
race_type_list_for_form = [(rt.id, rt.show_name)
                           for rt in RaceType.query.all()]


class ResultForm(FlaskForm):
    member_id = SelectField('参加者:', coerce=int, validators=[InputRequired()],
                            choices=visible_member_list_for_form)

    race_id = SelectField('大会:', coerce=int, validators=[InputRequired()],
                          choices=race_list_for_form)

    race_type_id = SelectField('種目:', coerce=int, validators=[InputRequired()],
                               choices=race_type_list_for_form)
    result = FloatField('記録:', validators=[InputRequired()])
    comment = TextAreaField('備考:', validators=[Optional()])
    confirmed = HiddenField(validators=[Optional()])
    method = HiddenField(validators=[Optional()])
    submit = SubmitField('確定', validators=[Optional()])


@app.route('/result/edit', methods=['GET', 'POST'])
@login_required
def result_edit():
    # app.logger.info(request.form)
    form = ResultForm(formdata=request.form)

    if form.validate_on_submit():
        return redirect(url_for('result_confirm'), code=307)

    if request.args.get('method') == 'PUT':
        race_id = int(request.args.get('race_id'))
        race_type_id = int(request.args.get('race_type_id'))
        member_id = int(request.args.get('member_id'))
        result = Result.query.get(
            {"race_id": race_id, "race_type_id": race_type_id, "member_id": member_id})
        form = ResultForm(obj=result)
        form.race = Race.query.get(race_type_id)
        form.method.data = 'PUT'

    else:
        race_id = int(request.args.get('race_id'))
        result = Result()
        result.race_id = race_id
        form = ResultForm(obj=result)
        form.race = Race.query.get(race_id)
        form.method.data = 'POST'

    return render_template('result_edit.html', form=form)


@app.route('/result/confirm', methods=['POST'])
@login_required
def result_confirm():
    form = ResultForm(formdata=request.form)
    app.logger.info(request.form)

    # form.visible.data = request.form.get('visible') != 'False'

    if request.form.get('submit') == 'キャンセル':
        return redirect(url_for('user'))

    race_id = int(form.race_id.data)
    race_type_id = int(form.race_type_id.data)
    member_id = int(form.member_id.data)

    if form.validate_on_submit() and request.form.get('confirmed'):
        if request.form.get('method') == 'DELETE':
            result = Result.query.get(
                {"race_id": race_id, "race_type_id": race_type_id, "member_id": member_id})
            db.session.delete(result)
        elif request.form.get('method') == 'PUT':
            result = Result.query.get(
                {"race_id": race_id, "race_type_id": race_type_id, "member_id": member_id})
            form.populate_obj(result)
        elif request.form.get('method') == 'POST':
            result = Result()
            form.populate_obj(result)
            db.session.add(result)
        db.session.commit()
        return redirect(url_for('result'))
    else:
        if request.form.get('method') == 'DELETE':
            result = Result.query.get(
                {"race_id": race_id, "race_type_id": race_type_id, "member_id": member_id})
            form = ResultForm(obj=result)
        form.member = Member.query.get(int(form.member_id.data))
        form.race_type = RaceType.query.get(int(form.race_type_id.data))
        form.race = Race.query.get(int(form.race_id.data))
        return render_template('result_confirm.html', form=form)
