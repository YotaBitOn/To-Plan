from PySide6.QtCore import QObject, Signal

class AppSignals(QObject):
    show_add_task_popup = Signal()

    update_progress_bar = Signal()
    update_task_info = Signal(str,str,str,str)

    complete_task = Signal(str)
    setEmptyPage = Signal(str)

    def __init__(self):
        super().__init__()



signals = AppSignals()

#signals.show_add_task_popup.connect(lambda : print('ee'))