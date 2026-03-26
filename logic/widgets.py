import datetime

from PySide6.QtGui import QIcon, QPainter, QColor
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QEvent, Qt, QPropertyAnimation, Property, QEasingCurve, Signal
from PySide6.QtWidgets import QWidget

#variables
from config.env_loader import task_widget_ui, task_step_ui
from config.constants import icons, palette, diff_col
from logic.appState import state

#funcs
from logic.core import convert_qtTime_int
from logic.signalHub import signals


class Task(QWidget):
    def __init__(self, taskId, name, description, difficulty, category, start_time, end_time, parent = None):
        super().__init__()

        state.cur_task = taskId

        self.id = taskId
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
            signals.update_task_info.emit(self.id)
            print(self.id)
    def deconstruct(self):
        signals.setEmptyPage.emit(self.name)

        self.task.setParent(None)
        self.task.deleteLater()
        del state.tasks[state.cur_task]

        del self

class TaskStep():
    def __init__(self, name='Step', parent=None):
        super().__init__()

        self.name = name
        self.taskstep = QUiLoader().load(task_step_ui, None)
        self.completed = False
        self.taskstep.stackedWidget.setCurrentIndex(1)
        self.taskstep.stackedWidget.setStyleSheet(f"""background-color: {palette['black']};""")
        self.taskstep.task_step_label.setText(self.name)

        self.taskstep.task_step_apply.clicked.connect(lambda : self.confirm_name())
        self.taskstep.task_step_check.clicked.connect(lambda : self.toggle_complete())
        self.taskstep.task_step_edit.clicked.connect(lambda : self.edit_name())
        self.taskstep.task_step_delete.clicked.connect(lambda : self.deconstruct())

    def confirm_name(self):
        self.name = self.taskstep.lineEdit.text()

        self.taskstep.stackedWidget.setCurrentIndex(0)
        self.taskstep.task_step_label.setText(self.name)

    def toggle_complete(self):
        self.completed = not self.completed

        if self.completed:
            self.taskstep.task_step_check.setIcon(QIcon('sources/icons_white/circle-check-big.svg'))
        else:
            self.taskstep.task_step_check.setIcon(QIcon('sources/icons_white/circle.svg'))

        state.tasks[state.cur_task]['taskSteps']['steps'][self] = self.completed

        signals.update_progress_bar.emit()

    def edit_name(self):
        self.taskstep.stackedWidget.setCurrentIndex(1)

    def deconstruct(self):
        self.taskstep.deleteLater()
        del state.tasks[state.cur_task]['taskSteps']['steps'][self]

        signals.update_progress_bar.emit()
        del self


class AnimatedToggle(QWidget):
    toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 26)

        self._checked = False
        self._offset = 2

        self.anim = QPropertyAnimation(self, b"offset", self)
        self.anim.setDuration(180)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

    def mousePressEvent(self, event):
        self.on_click()

    def on_click(self):
        self._checked = not self._checked

        self.anim.stop()
        self.anim.setStartValue(self._offset)
        self.anim.setEndValue(26 if self._checked else 2)
        self.anim.start()

        self.toggled.emit(self._checked)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # background
        bg = QColor("#4CAF50") if self._checked else QColor("#777")
        p.setBrush(bg)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, self.width(), self.height(), 13, 13)

        p.setBrush(Qt.white)
        p.drawEllipse(self._offset, 2, 22, 22)

    def getOffset(self):
        return self._offset

    def setOffset(self, value):

        self._offset = value

        self.update()

    offset = Property(float, getOffset, setOffset)

    def isChecked(self):
        return self._checked
