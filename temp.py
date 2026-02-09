import sys

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication

loader = QUiLoader()

app = QApplication(sys.argv)
mw = loader.load('task.ui', None)



mw.show()
app.exec()