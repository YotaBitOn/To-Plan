import datetime
from config.env_loader import data
from PySide6.QtCore import QDate, QDateTime, QTime

#variables

def calculate_next_occurrence_raw(rep_type, rep_vals, at_time):
    cur_date = QDate.currentDate()

    next_occurrence = 0

    if rep_type == 1:

        cur_datetime_stamp = QDateTime(cur_date, QTime(0, 0, 0)).toSecsSinceEpoch() + at_time

        next_occurrence = cur_datetime_stamp + 86400 * rep_vals[0]

    elif rep_type == 2:
        return 0
        pass#gonnado later

    elif rep_type == 3:
        cur_mounth = QDate(cur_date.year(), cur_date.month(), 1)
        cur_mounth_stamp = QDateTime(cur_mounth, QTime(0, 0, 0)).toSecsSinceEpoch() + at_time

        next_occurrence = cur_mounth_stamp + 86400 * (rep_vals[0]-1)
    elif rep_type == 4:
        cur_year = QDate(cur_date.year(), 1, 1)
        cur_year_stamp = QDateTime(cur_year, QTime(0, 0, 0)).toSecsSinceEpoch() + at_time

        req_date = QDate(cur_date.year()+1, data['mounth_number'][rep_vals[1]], int(rep_vals[0]))

        next_occurrence = cur_year_stamp + 86400 * cur_year.daysTo(req_date)

    elif rep_type == 0:
        cur_datetime = QDateTime(cur_date, QTime(0, 0, 0)).toSecsSinceEpoch() + at_time
        next_occurrence = cur_datetime + 86400

    return next_occurrence

def calculate_next_occurrence(rep_type, at_time, caller):
    cur_date = QDate.currentDate()
    rep_vals = []

    next_occurrence = 0

    if rep_type == 'Few Days':

        cur_datetime_stamp = QDateTime(cur_date, at_time).toSecsSinceEpoch()

        value = int(caller.ui.few_days_edit.text())
        rep_vals.append(value)

        next_occurrence = cur_datetime_stamp + 86400 * value

    elif rep_type == 'Week':
        return 0
        pass#gonnado later

    elif rep_type == 'Mounth':
        cur_mounth = QDate(cur_date.year(), cur_date.month(), 1)
        cur_mounth_stamp = QDateTime(cur_mounth, at_time).toSecsSinceEpoch()

        value = int(caller.ui.day_edit_2.text())
        rep_vals.append(value)

        next_occurrence = cur_mounth_stamp + 86400 * (value-1)
    elif rep_type == 'Year':
        cur_year = QDate(cur_date.year(), 1, 1)
        cur_year_stamp = QDateTime(cur_year, at_time).toSecsSinceEpoch()

        day_value = int(caller.ui.day_edit.text())
        mounth_value = data['mounth_number'][caller.ui.mounth_edit.currentText()]

        rep_vals.append(day_value)
        rep_vals.append(caller.ui.mounth_edit.currentText())

        req_date = QDate(cur_date.year()+1, mounth_value, day_value)

        next_occurrence = cur_year_stamp + 86400 * cur_year.daysTo(req_date)

    elif rep_type == 'Day':
        cur_datetime = QDateTime(cur_date, at_time).toSecsSinceEpoch()
        next_occurrence = cur_datetime + 86400

    return next_occurrence, rep_vals

def convert_qtTime_str(qt_Time):
    cur_date = QDate.currentDate()
    time = QDateTime(cur_date, qt_Time).toSecsSinceEpoch()

    return time

def convert_qtTime_int(qt_Time):
    return qt_Time.hour() * 3600 + qt_Time.minute() * 60 + qt_Time.second()

def datetime_str(datetime_stamp):

    return datetime.datetime.fromtimestamp(datetime_stamp).strftime('%d.%m.%Y')
