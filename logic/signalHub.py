from PySide6.QtCore import QObject, Signal

class AppSignals(QObject):
    update_progressBar = Signal()

signals = AppSignals()