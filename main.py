import sqlite3
import sys
import datetime

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication

import AnimatedToggle

mw = popup = None
cur_main_ui = "v21.ui"
cur_popup_ui = "add_task_popup_v6.ui"

def check_connection():
    print('Hello, World!')

def set_repeatable_menu():
    global popup
    popup.repeatable_widget.setVisible(popup.repeatable_toggle._checked)

def submit():
    global popup
    _task_name = popup.name_edit.text()
    _task_description = popup.description_edit.toPlainText()
    _task_due = str(popup.timeEdit.time())
    print(_task_due)
    _task_difficulty = popup.diff_box.currentText()
    _task_category= popup.difficulty_combobox.currentText() # rename it pls

    #change user
    start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    end_time = datetime.datetime.now().strftime('%Y-%m-%d') + _task_due #change with adding repeatable
    cursor.execute("""
    INSERT INTO users
    (user, taskName, start_time, end_time, difficulty, category, completed, repeatable)
    VALUES (?,?,?,?,?,?,?,?)""",
    ('Yasinets',_task_name,start_time,end_time,_task_difficulty,_task_category,0,popup.repeatable_toggle._checked))
    #conn.commit() <-----------IMPORTANT (off for test cases)
    global mw
    mw.stackedWidget.setVisible(True)

    mw.stackedWidget.setCurrentIndex(0)
    mw.category_stack.setCurrentIndex(0)
    mw.difficulty_stack.setCurrentIndex(0)
    mw.description_label_edit_layout_2.setCurrentIndex(0) #rename

    mw.task_name_label.setText(_task_name)
    mw.category.setText(_task_category)
    mw.difficulty.setText(_task_difficulty) # RENAME THEIR LABELS
    mw.description_input_label_2.setText(_task_description) #rename

    popup.close()
    popup = None
    #add repeatable
def show_add_task_popup():
    global popup

    popup = loader.load(cur_popup_ui, None)


    #popup.setStretch(1,1,1,1,1,1,1,1)

    popup.repeatable_widget.setVisible(False)
    popup.repeatable_toggle = AnimatedToggle.AnimatedToggle(popup)
    popup.repeatable_layout.replaceWidget(popup.rep_switch, popup.repeatable_toggle)
    popup.repeatable_toggle.toggled.connect(set_repeatable_menu)

    popup.submit_button.clicked.connect(submit)

    popup.show()



conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

loader = QUiLoader()

app = QApplication(sys.argv)
mw = loader.load(cur_main_ui, None)

mw.stackedWidget.setVisible(False)
mw.tabWidget.setCurrentIndex(0)
mw.add_task_button.clicked.connect(show_add_task_popup)

mw.show()
app.exec()