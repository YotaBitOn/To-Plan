import sqlite3, seaborn as sns, matplotlib.pyplot as plt
import os
from collections import defaultdict

from PySide6.QtCharts import QLineSeries, QChart, QDateTimeAxis, QValueAxis
from PySide6.QtCore import QDateTime, Qt

from config.env_loader import drop_db_mode

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, './user_data.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

if not drop_db_mode:
    cursor.execute("SELECT * FROM users")

    data = cursor.fetchall()

else:
    data = []

class MyPlot():
    def __init__(self):
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.setAxis()
        self.print_data()

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
        for task in data:
            print(task)

    def tasks_created_plot(self, accumulation = False):
        if len(data) == 0:
            return
        stats = defaultdict(lambda: {"created": 0, "completed": 0})

        for task in data:
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


#x,y = tasks_created_plot(0)
#
#sns.lineplot(x=x,y=y)
#plt.show()