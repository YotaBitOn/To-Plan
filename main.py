import sqlite3
import sys

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication

print('Hello, World!')
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

loader = QUiLoader()

app = QApplication(sys.argv)
mw = loader.load('main_v19.ui', None)

mw.show()
app.exec()