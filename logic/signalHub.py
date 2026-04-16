from PySide6.QtCore import QObject, Signal

class AppSignals(QObject):
    show_add_task_popup = Signal()

    update_progress_bar = Signal()
    update_task_info = Signal(str)

    complete_task = Signal(str)
    setEmptyPage = Signal(str)

    change_theme = Signal()
    change_lang = Signal()
    def __init__(self):
        super().__init__()



signals = AppSignals()
