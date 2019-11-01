from flask import render_template, request, abort, redirect, url_for
from honomara_members_site import app, db
from honomara_members_site.login import user_check, users
from honomara_members_site.model import Member, Training, After, Restaurant, Race, RaceBase, RaceType, Result
from honomara_members_site.form import MemberForm, TrainingForm, AfterForm, RaceBaseForm, RaceForm, ResultForm
from flask_login import login_required, login_user, logout_user


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login/', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        if (request.form["username"] in user_check and
                request.form["password"] == user_check[request.form["username"]]["password"]):
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


@app.route('/member/')
@login_required
def member():
    members = Member.query.order_by(Member.year.desc())
    return render_template('member.html', members=members)


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


@app.route('/result/edit', methods=['GET', 'POST'])
@login_required
def result_edit():
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
