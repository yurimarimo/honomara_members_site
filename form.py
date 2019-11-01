from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, IntegerField, FloatField
from wtforms import HiddenField, TextAreaField, DateField, SelectMultipleField, SelectField
from wtforms.validators import Optional, InputRequired
from honomara_members_site.model import Member, Restaurant, RaceBase, Race, RaceType


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

restaurants_choices = [(r.id, "{}({})".format(
    r.restaurant_name, r.place)) for r in Restaurant.query.all()]


race_base_list_for_form = [(r.race_name, r.race_name)
                           for r in RaceBase.query.all()]


race_list_for_form = [(r.id, r.race_name) for r in Race.query.all()]
race_type_list_for_form = [(rt.id, rt.show_name)
                           for rt in RaceType.query.all()]


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
