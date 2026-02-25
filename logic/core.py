from PySide6.QtCore import QDate, QDateTime

#variables
from config.time_constans import mounth_number


def calculate_next_occurrence(rep_type, at_time, caller):
    cur_date = QDate.currentDate()
    rep_vals = []

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
        mounth_value = mounth_number[caller.ui.mounth_edit.currentText()]

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
