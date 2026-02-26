import datetime

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget

#variables
from config.env_loader import task_widget_ui
from config.ui_constants import icons, palette, diff_col
from logic.appState import state

#funcs
from logic.core import convert_qtTime_str
from logic.signalHub import signals


class Task(QWidget):
    def __init__(self,name, description, difficulty, category, start_time, end_time, parent = None):
        super().__init__()

        state.cur_task = name

        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.category = category

        self.task = QUiLoader().load(task_widget_ui, None)

        self.task.setMaximumHeight(120)
        self.task.task_name.setText(name)

        self.start_time = start_time
        self.end_time  = end_time

        self.task.task_duration.setText(f'{datetime.datetime.fromtimestamp(self.start_time).strftime("%H:%M")} - {datetime.datetime.fromtimestamp(self.end_time).strftime("%H:%M")}')
        self.task.categ_icon.setIcon(QIcon(f"sources/icons_white/{icons[category]}"))
        bg_color = palette[diff_col[difficulty]]
        self.task.setStyleSheet(f"""background-color: {bg_color}; border-radius: 20px;""")

        self.task.setMouseTracking(True)
        self.task.setAttribute(Qt.WA_StyledBackground, True)


        self.task.installEventFilter(self)
        self.task.task_check.clicked.connect(lambda : signals.complete_task.emit(self.name))

        if parent:
            parent.layout().addWidget(self.task)

    def update_duration(self):
        self.task.task_duration.setText(f'{datetime.datetime.fromtimestamp(self.start_time).strftime("%H:%M")} - {datetime.datetime.fromtimestamp(self.end_time).strftime("%H:%M")}')

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            signals.update_task_info.emit(self.name, self.description, self.difficulty, self.category)
    def deconstruct(self):
        signals.setEmptyPage.emit(self.name)

        self.task.setParent(None)
        self.task.deleteLater()
        del state.tasks[state.cur_task]

        del self

