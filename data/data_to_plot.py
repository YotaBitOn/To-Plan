import random
import sqlite3
import os
from collections import defaultdict

from PySide6.QtCharts import QLineSeries, QChart, QDateTimeAxis, QValueAxis, QPieSeries, QStackedBarSeries, QBarSet, \
    QBarCategoryAxis
from PySide6.QtCore import QDateTime, Qt
from PySide6.QtGui import QColor

from config.env_loader import drop_db_mode, data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, './user_data.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

if not drop_db_mode:
    cursor.execute("SELECT * FROM users")

    db_data = cursor.fetchall()

else:
    db_data = []

class MyPlot():
    def __init__(self):
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        #self.print_data()
    def setAxis(self):
        self.axisX = QDateTimeAxis()
        self.axisX.setFormat("dd.MM.yyyy")
        self.axisX.setTitleText("Дата")

        self.chart.addAxis(self.axisX, Qt.AlignBottom)

        self.axisY = QValueAxis()
        self.axisY.setTitleText("Показник")
        self.axisY.setLabelFormat("%d")

        self.chart.addAxis(self.axisY, Qt.AlignLeft)

    def print_data(self):
        for task in db_data:
            print(task)

    def tasks_created_plot(self, accumulation = False):
        self.setAxis()

        if len(db_data) == 0:
            return
        stats = defaultdict(lambda: {"created": 0, "completed": 0})

        for task in db_data:
            date = task[3]
            completed = int(task[8])
            stats[date]["created"] += 1
            stats[date]["completed"] += completed

        x = sorted(
            stats.keys(),
            key=lambda d: QDateTime.fromString(d, "dd.MM.yyyy")
        )

        created_y = []
        completed_y = []

        for d in x:
            created_y.append(stats[d]["created"])
            completed_y.append(stats[d]["completed"])

        if accumulation:
            for i in range(1, len(created_y)):
                created_y[i] += created_y[i - 1]
                completed_y[i] += completed_y[i - 1]


        t_created = QLineSeries()
        t_completed = QLineSeries()

        for d_str, val in zip(x, created_y):
            dt = (QDateTime.fromString(d_str, "dd.MM.yyyy"))
            t_created.append(dt.toMSecsSinceEpoch(), val)

        for d_str, val in zip(x, completed_y):
            dt = (QDateTime.fromString(d_str, "dd.MM.yyyy"))
            t_completed.append(dt.toMSecsSinceEpoch(), val)


        self.chart.addSeries(t_created)
        self.chart.addSeries(t_completed)

        self.axisX.setTickCount(min(len(x), 10))
        max_val = max(created_y + completed_y)
        self.axisY.setRange(0, max_val)

        t_created.attachAxis(self.axisX)
        t_completed.attachAxis(self.axisX)

        t_created.attachAxis(self.axisY)
        t_completed.attachAxis(self.axisY)

    def completed_ratio(self):
        #('piEZSKOuxCHKJYbnPgMKm', 'Yasinets', 'Task #0', '16.04.2026', 0, 0, 'very_easy', 'sport', 0, 0, None, '', '',
        # '', 1776333835.380634, 0)

        completed_ammo = sum([d[8] for d in db_data])
        not_completed_ammo = len(db_data) - completed_ammo

        completed_pie = QPieSeries()
        completed_pie.append("Not Completed", not_completed_ammo)
        completed_pie.append("Completed", completed_ammo)

        slices = completed_pie.slices()

        for slice in completed_pie.slices():
            slice.hovered.connect(lambda state, s=slice: self.pie_on_hovered(s, state))


        self.chart.addSeries(completed_pie)
        self.chart.legend().setAlignment(Qt.AlignBottom)

    def diff_ratio(self):
        diffs = [d[6] for d in db_data]

        diff_pie = QPieSeries()

        added = set()
        for diff in diffs:
            if diff not in added:
                slice = diff_pie.append(f"{diff}",diffs.count(diff))

                color = data['diff_col'][diff]
                r,g,b = map(int, data['palette'][color].split(','))
                slice.setBrush(QColor(r,g,b))

                added.add(diff)

        for slice in diff_pie.slices():
            slice.hovered.connect(lambda state, s=slice: self.pie_on_hovered(s, state))

        self.chart.addSeries(diff_pie)
        self.chart.legend().setAlignment(Qt.AlignBottom)

    def categ_ratio(self):
        categs = [d[7] for d in db_data]

        categ_pie = QPieSeries()

        added = set()
        banned_colors = ["239, 239, 239", "215, 215, 215", "190, 190, 190", "65, 65, 65", "40, 40, 40", "16, 16, 16"]
        for categ in categs:
            if categ not in added:

                slice = categ_pie.append(f"{categ}",categs.count(categ))

                color = data['categ_col'][categ]
                r, g, b = map(int, data['palette'][color].split(','))
                slice.setBrush(QColor(r,g,b))

                added.add(categ)
        for slice in categ_pie.slices():
            slice.hovered.connect(lambda state, s=slice: self.pie_on_hovered(s, state))

        self.chart.addSeries(categ_pie)
        self.chart.legend().setAlignment(Qt.AlignBottom)

    def day_diff_ratio(self):
        if len(db_data) == 0:
            return

        day_diff_bar = QStackedBarSeries()

        hash =  [[task[3], task[6]] for task in db_data]
        hash = sorted(hash, key=lambda x: x[0]) #change to qdate
        dates = sorted(list(set([h[0] for h in hash])))

        bar_very_easy = QBarSet("very_easy")
        bar_easy = QBarSet("easy")
        bar_medium = QBarSet("medium")
        bar_hard = QBarSet("hard")

        color = data['diff_col']['very_easy']
        r, g, b = map(int, data['palette'][color].split(','))
        bar_very_easy.setBrush(QColor(r, g, b))

        color = data['diff_col']['easy']
        r, g, b = map(int, data['palette'][color].split(','))
        bar_easy.setBrush(QColor(r, g, b))

        color = data['diff_col']['medium']
        r, g, b = map(int, data['palette'][color].split(','))
        bar_medium.setBrush(QColor(r, g, b))

        color = data['diff_col']['hard']
        r, g, b = map(int, data['palette'][color].split(','))
        bar_hard.setBrush(QColor(r, g, b))


        for date in dates:

            very_easy_ammo = sum(1 for d in db_data if ((d[3] == date) and (d[6] == 'very_easy')))
            easy_ammo = sum(1 for d in db_data if ((d[3] == date) and (d[6] == 'easy')))
            medium_ammo = sum(1 for d in db_data if ((d[3] == date) and (d[6] == 'medium')))
            hard_ammo = sum(1 for d in db_data if ((d[3] == date) and (d[6] == 'hard')))

            bar_very_easy << very_easy_ammo
            bar_easy << easy_ammo
            bar_medium << medium_ammo
            bar_hard << hard_ammo

        day_diff_bar.append(bar_very_easy)
        day_diff_bar.append(bar_easy)
        day_diff_bar.append(bar_medium)
        day_diff_bar.append(bar_hard)

        self.chart.addSeries(day_diff_bar)

        axis = QBarCategoryAxis()
        axis.append(dates)
        self.chart.addAxis(axis, Qt.AlignBottom)
        day_diff_bar.attachAxis(axis)

    def day_categ_ratio(self):
        if len(db_data) == 0:
            return

        day_categ_bar = QStackedBarSeries()

        hash =  [[task[3], task[7]] for task in db_data]
        hash = sorted(hash, key=lambda x: x[0]) #change to qdate
        dates = sorted(list(set([h[0] for h in hash])))
        print(dates)
        categs = []

        for categ in data['categ_col']:
            categ_bar = QBarSet(categ)

            color = data['categ_col'][categ]
            r, g, b = map(int, data['palette'][color].split(','))
            categ_bar.setBrush(QColor(r, g, b))

            categs.append([categ,categ_bar])


        for date in dates:

            for categ in range( len(categs) ):
                categ_name = categs[categ][0]

                categ_ammo = sum(1 for d in db_data if ((d[3] == date) and (d[7] == categ_name)))

                categs[categ][1] << categ_ammo

        for categ in range( len(categs) ):
            day_categ_bar.append(categs[categ][1] << categ_ammo)

        self.chart.addSeries(day_categ_bar)

        axis = QBarCategoryAxis()
        axis.append(dates)
        self.chart.addAxis(axis, Qt.AlignBottom)
        day_categ_bar.attachAxis(axis)

    def pie_on_hovered(self, slice, state):
        slice.setExploded(state)
        slice.setLabelVisible(state)

