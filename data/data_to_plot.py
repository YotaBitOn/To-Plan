import sqlite3, seaborn as sns, matplotlib.pyplot as plt
import os

from PySide6.QtCharts import QLineSeries, QChart, QDateTimeAxis, QValueAxis
from PySide6.QtCore import QDateTime, Qt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, './user_data.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()


cursor.execute("SELECT * FROM users")

data = cursor.fetchall()

def print_data():
    for task in data:
        print(task)

def tasks_created_plot(accumulation = False):
    dates = [task[3] for task in data]

    x = []
    y = []
    y_accum = []
    for date in dates:
        if date not in x:
            x.append(date)
            y.append(dates.count(date))
            y_accum.append(sum(y))

    if accumulation:
        y = y_accum

    series = QLineSeries()

    for d_str, val in zip(x, y):
        # Перетворюємо рядок у QDateTime, а потім у мілісекунди
        dt = (
            QDateTime.fromString(d_str, "dd.MM.yyyy"))
        series.append(dt.toMSecsSinceEpoch(), val)

    chart = QChart()
    chart.addSeries(series)

    axis_x = QDateTimeAxis()
    axis_x.setFormat("dd.MM.yyyy")  # Формат відображення (напр. 01 Jan 2023)
    axis_x.setTitleText("Дата")
    axis_x.setTickCount(len(x))  # Кількість позначок на осі
    chart.addAxis(axis_x, Qt.AlignBottom)
    series.attachAxis(axis_x)

    # --- Налаштування осі Y (Числа) ---
    axis_y = QValueAxis()
    axis_y.setTitleText("Показник")
    axis_y.setLabelFormat("%d")  # Ціле число
    chart.addAxis(axis_y, Qt.AlignLeft)
    series.attachAxis(axis_y)

    return chart
#x,y = tasks_created_plot(0)
#
#sns.lineplot(x=x,y=y)
#plt.show()