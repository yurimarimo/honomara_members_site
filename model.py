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

    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), primary_key=True)
    training_id = db.Column(db.Integer, db.ForeignKey('trainings.training_id'), primary_key=True)

    def __repr__(self):
        return "<TrainingParticipant(training_id:{}, member_id:{})>".\
            format(self.training_id, self.member_id)


class Training(db.Model):
    __tablename__ = 'trainings'

    training_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    wday = db.Column(db.String(1))
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

    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), primary_key=True)
    after_id = db.Column(db.Integer, db.ForeignKey('afters.after_id'), primary_key=True)

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
    after_stage = db.Column(db.Integer, nullable=False, server_default=db.text('1'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.restaurant_id'), nullable=False)
    total = db.Column(db.Integer)
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
