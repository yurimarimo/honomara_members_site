from flask import render_template as flask_render_template
from datetime import date, datetime
from locale import setlocale, LC_TIME


setlocale(LC_TIME, 'ja_JP.UTF-8')  # for get_wday


def render(template, **args):
    args['template'] = template
    return flask_render_template('flame.html', **args)


def year_to_grade(year, current_school_year):
    return current_school_year + 1 - year


def get_school_year(date):
    if date.month < 4:
        return date.year - 1
    else:
        return date.year


def str_to_date(str):
    return datetime.strptime(str, '%Y-%m-%d').date()


def get_wday(date):
    return date.strftime('%a')


current_school_year = get_school_year(date.today())
