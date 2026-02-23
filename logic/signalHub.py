from PySide6.QtCore import QObject, Signal

class AppSignals(QObject):
    update_progress_bar = Signal()
    update_task_info = Signal(str,str,str,str)
    complete_task = Signal(str)
signals = AppSignals()