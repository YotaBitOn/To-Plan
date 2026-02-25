from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader

#variables
from config.env_loader import task_step_ui
from config.ui_constants import palette
from logic.appState import state

#funcs
from logic.signalHub import signals

class TaskStep():
    def __init__(self, parent=None):
        super().__init__()


        self.taskstep = QUiLoader().load(task_step_ui, None)
        self.completed = False
        self.taskstep.stackedWidget.setCurrentIndex(1)
        self.taskstep.stackedWidget.setStyleSheet(f"""background-color: {palette['black']};""")

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




