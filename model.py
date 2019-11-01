from honomara_members_site import app
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(app)


class Member(db.Model):
    __tablename__ = 'members'

    member_id = db.Column(db.Integer, primary_key=True)
    family_name = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    show_name = db.Column(db.String(20), nullable=False)
    kana = db.Column(db.String(40), nullable=False)
    family_kana = db.Column(db.String(20), nullable=True)
    first_kana = db.Column(db.String(20), nullable=True)
    year = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.Integer, nullable=False)
    visible = db.Column(db.Boolean, nullable=False)

    results = db.relationship('Result')

    def __init__(self, form=None, **args):
        return super().__init__(**args)

    def __repr__(self):
        fields = {}
        fields['member_id'] = self.member_id
        fields['family_name'] = self.family_name
        fields['first_name'] = self.first_name
        fields['show_name'] = self.show_name
        fields['year'] = self.year
        if self.sex == 0:
            fields['sex'] = 'male'
        elif self.sex == 1:
            fields['sex'] = 'female'
        else:
            fields['sex'] = 'unknown or other'
        fields['visible'] = self.visible
        return "<Member('{member_id}','{family_name}', '{first_name}', '{show_name}', {year}, {sex}, {visible})>".format(**fields)


class TrainingParticipant(db.Model):
    __tablename__ = 'training_participants'

    member_id = db.Column(db.Integer, db.ForeignKey(
        'members.member_id'), primary_key=True)
    training_id = db.Column(db.Integer, db.ForeignKey(
        'trainings.training_id'), primary_key=True)

    def __repr__(self):
        return "<TrainingParticipant(training_id:{}, member_id:{})>".\
            format(self.training_id, self.member_id)


class Training(db.Model):
    __tablename__ = 'trainings'

    training_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    place = db.Column(db.String(20), nullable=False)
    weather = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text)

    participants = db.relationship(
        'Member',
        secondary=TrainingParticipant.__tablename__,
        order_by='Member.year, Member.kana'
    )

    def __init__(self, form=None, **args):
        return super().__init__(**args)

    def __repr__(self):
        return "<Training(training_id:{}, {:%Y-%m-%d}, place:{}, title:'{}')>"\
            .format(self.training_id, self.date, self.place, self.title)


class AfterParticipant(db.Model):
    __tablename__ = 'after_participants'

    member_id = db.Column(db.Integer, db.ForeignKey(
        'members.member_id'), primary_key=True)
    after_id = db.Column(db.Integer, db.ForeignKey(
        'afters.after_id'), primary_key=True)

    def __repr__(self):
        return "<AfterParticipant(after_id:{}, member_id:{})>".\
            format(self.after_id, self.member_id)


class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    restaurant_id = db.Column(db.Integer, primary_key=True)
    restaurant_name = db.Column(db.String(64), nullable=False)
    place = db.Column(db.String(20))
    comment = db.Column(db.Text)

    def __repr__(self):
        return "<Restaurant(id:{}, name:{}, plase:{})>".\
            format(self.restaurant_id, self.restaurant_name, self.place)


class After(db.Model):
    __tablename__ = 'afters'

    after_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    after_stage = db.Column(db.Integer, nullable=False,
                            server_default=db.text('1'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey(
        'restaurants.restaurant_id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    comment = db.Column(db.Text)
    restaurant = db.relationship('Restaurant')

    participants = db.relationship(
        'Member',
        secondary=AfterParticipant.__tablename__,
        order_by='Member.year, Member.kana'
    )

    def __init__(self, form=None, **args):
        return super().__init__(**args)

    def __repr__(self):
        return "<After(after_id:{}, {:%Y-%m-%d}, title:'{}')>".\
            format(self.after_id, self.date, self.title)


class RaceBase(db.Model):
    __tablename__ = 'race_bases'

    race_name = db.Column(db.String(100), primary_key=True)
    prefecture = db.Column(db.String(100))
    comment = db.Column(db.Text)
    races = db.relationship("Race")
    def __init__(self, form=None, **args):
        return super().__init__(**args)

    def __repr__(self):
        return "<RaceBase(race_name:{}, prefecture:{}, comment:'{}')>".\
            format(self.race_name, self.prefecture, self.comment)


class Race(db.Model):
    __tablename__ = 'races'

    race_id = db.Column(db.Integer, primary_key=True)
    race_name = db.Column(db.String(100), db.ForeignKey('race_bases.race_name'))
    date = db.Column(db.Date, nullable=False)

    results = db.relationship('Result',
                              backref="race",
                              order_by='Result.result'
                              )
    comment = db.Column(db.Text)

    def __init__(self, form=None, **args):
        return super().__init__(**args)

    def __repr__(self):
        return "<Race(race_id:{},race_name:{},date {:%Y-%m-%d}, results:{}, comment:'{}')>".\
            format(self.race_id, self.race_name, self.date,
                   len(self.results), self.comment)


class RaceType(db.Model):
    __tablename__ = 'race_types'

    race_type_id = db.Column(db.Integer, primary_key=True)
    race_type = db.Column(db.String(30))
    show_name = db.Column(db.String(30))
    ranking = db.Column(db.Integer)
    duration = db.Column(db.Float)
    distance = db.Column(db.Float)
    comment = db.Column(db.Text)
    results = db.relationship('Result')

    def __init__(self, form=None, **args):
        return super().__init__(**args)

    def __repr__(self):
        return "<RaceType(race_type_id:{}, race_type:{}, show_name:{}, ranking:{}, duration:{}, distance:{}, comment:'{}')>".\
            format(self.race_type_id, self.race_type, self.show_name,
                   self.ranking, self.duration, self.distance, self.comment[::])


class Result(db.Model):
    __tablename__ = 'results'

    member_id = db.Column(db.Integer, db.ForeignKey(
        'members.member_id'), primary_key=True)
    member = db.relationship('Member')

    race_id = db.Column(db.Integer, db.ForeignKey(
        'races.race_id'), primary_key=True)
    # race by backref

    race_type_id = db.Column(db.Integer, db.ForeignKey(
        'race_types.race_type_id'), primary_key=True)
    race_type = db.relationship('RaceType')

    result = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

    def __repr__(self):
        return "<Result(race:{}({:%Y-%m-%d}), race_type:{}, member:{}, result:{}, comment:{})>".\
            format(self.race.race_name, self.race.date, self.race_type.race_type,
                   self.member.show_name, self.result, self.comment)
