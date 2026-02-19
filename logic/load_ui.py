from PySide6.QtUiTools import QUiLoader

from config.env_loader import *

popup = QUiLoader().load(popup_ui, None)
task = QUiLoader().load(task_widget_ui, None)
taskstep = QUiLoader().load(task_step_ui, None)


