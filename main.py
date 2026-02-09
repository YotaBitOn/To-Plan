import sqlite3
import sys
import datetime

from PySide6.QtGui import QIcon, Qt
from PySide6.QtCore import QEvent, QObject
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QWidget

import AnimatedToggle

tasks = {}
diff_col = {
'Easy' : 'green',
'Medium' : 'yellow',
'Hard' : 'red',
'Free' : 'blue'
}
palette = {
'red' : 'rgb(211, 0, 0)',
'yellow' :'rgb(209, 167, 0)',
'gold' : 'rgb(214, 150, 0)',
'green' : 'rgb(49, 255, 34)',
'blue' : 'rgb(0, 179, 255)',
'gray' : 'rgb(40,40, 40)',
'black' :'rgb(16,16,16)'
}

icons = {
'Chores' : 'brush-cleaning(3).svg',
'Sport' : 'dumbbell.svg',
'Education' : 'graduation-cap.svg',
'Job' : 'hand-coins.svg',
'Meal' : 'utensils-crossed.svg'
}
mw = popup = None
cur_task = None

task_widget_ui = "task_v4.ui"
main_ui = "v23.ui"
popup_ui = "add_task_popup_v6.ui"
task_step_ui = 'task_step.ui'
class TaskStep(QWidget):
    def __init__(self):
        super.__init__()

        self.taskstep = loader.load(task_step_ui, mw.verticalLayout_3)



class Task(QWidget):
    def __init__(self,name, description, difficulty, category, repeatable = 0,parent = None):
        super().__init__()
        global mw, cur_task

        cur_task = name
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.category = category

        self.task = loader.load(task_widget_ui,parent)

        self.task.setMaximumHeight(120)
        self.task.task_name_8.setText(name)
        if description == '':
            self.task.task_description_8.setVisible(False)
        else:
            self.task.task_description_8.setText(description)
        self.task.toolButton_2.setIcon(QIcon(f"icons_white/{icons[category]}"))
        bg_color = palette[diff_col[difficulty]]
        self.task.setStyleSheet(f"""background-color: {bg_color}; border-radius: 20px;""")

        self.task.setMouseTracking(True)
        self.task.setAttribute(Qt.WA_StyledBackground, True)


        self.task.installEventFilter(self)
        parent.layout().addWidget(self.task)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            set_task_info(self.name, self.description, self.difficulty, self.category)



def check_connection():
    print('Hello, World!')

def set_task_info(task_name, task_description, task_difficulty, task_category):
    global mw, cur_task

    cur_task = task_name

    mw.stackedWidget.setVisible(True)

    mw.stackedWidget.setCurrentIndex(0)
    mw.category_stack.setCurrentIndex(0)
    mw.difficulty_stack.setCurrentIndex(0)
    mw.description_label_edit_layout.setCurrentIndex(0)

    mw.task_name_label.setText(task_name)
    mw.category.setText(task_category)
    mw.difficulty.setText(task_difficulty)  # RENAME THEIR LABELS
    mw.description_input_label.setText(task_description)

    mw.steps_label.setText(f'{task_name} steps')

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

    set_task_info(_task_name, _task_description, _task_difficulty, _task_category)

    task = Task(_task_name, _task_description, _task_difficulty, _task_category, popup.repeatable_toggle._checked, parent=mw.tasks_scrollwidget)

    tasks[_task_name] = task

    popup.close()
    popup = None
    #add repeatable

def show_add_task_popup():
    global popup

    popup = loader.load(popup_ui, None)

    #popup.setStretch(1,1,1,1,1,1,1,1)

    popup.repeatable_widget.setVisible(False)
    popup.repeatable_toggle = AnimatedToggle.AnimatedToggle(popup)
    popup.repeatable_layout.replaceWidget(popup.rep_switch, popup.repeatable_toggle)
    popup.repeatable_toggle.toggled.connect(set_repeatable_menu)

    popup.submit_button.clicked.connect(submit)

    popup.show()

def add_task_step():
    task_step = TaskStep()

conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

loader = QUiLoader()

app = QApplication(sys.argv)
mw = loader.load(main_ui, None)

mw.stackedWidget.setVisible(False)
mw.tabWidget.setCurrentIndex(0)
mw.add_task_button.clicked.connect(show_add_task_popup)
mw.add_task_step_buttonclicked.connect(add_task_step)

mw.show()
app.exec()