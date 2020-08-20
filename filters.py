from honomara_members_site import app, db


def fmt_course(course, long=False):
    show_name = course.show_name
    distance = course.distance
    time = course.time
    t = course.type
    ret = show_name
    if t == 'road':
        if long:
            if ret:
                ret += '({}km ロード)'.format(distance)
            else:
                ret = '{}kmロード'.format(distance)
        elif not ret:
            ret = '{}km'.format(int(distance))
    elif t == 'trail':
        if long and ret:
            ret += '({}km トレイル)'.format(distance)
        elif not ret:
            ret = '{}kmトレイル'.format(int(distance))
    elif t == 'time':
        if not ret:
            ret = '{}時間走'.format(int(distance))
    elif t == 'relay':
        if not ret:
            ret = '{}時間リレー'.format(int(distance))

    if not ret:
        ret = '不明種目({}km ,{}時間, {})'.format(distance, time, t)
    return ret


def fmt_time(time, long=False):
    if time is None:
        return "未入力"
    ms = time % 1000
    time //= 1000
    s = time % 60
    time //= 60
    m = time % 60
    time //= 60
    h = time
    ret = ''
    if h > 0:
        ret += '{}°'.format(h)
    if h > 0 or m > 0:
        ret += "{:02}′".format(m)
    ret += '{:02}'.format(s)
    if long:
        ret += '″{:02}'.format(ms)
    return ret


app.jinja_env.filters["fmt_course"] = fmt_course
app.jinja_env.filters["fmt_time"] = fmt_time
