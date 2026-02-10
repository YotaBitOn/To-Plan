import sqlite3
import sys
import datetime

from PySide6.QtGui import QIcon, Qt
from PySide6.QtCore import QEvent, QObject
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout

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
task_ammo = 0

task_widget_ui = "task_v4.ui"
main_ui = "v23.ui"
popup_ui = "add_task_popup_v6.ui"
task_step_ui = 'task_step_v3.ui'
#cursor
class TaskStep(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        global mw

        self.taskstep = loader.load(task_step_ui, self)
        self.completed = False
        #self.taskstep.raise_()
        self.taskstep.stackedWidget.setCurrentIndex(1)
        self.taskstep.stackedWidget.setStyleSheet(f"""background-color: {palette['black']};""")

        self.taskstep.task_step_apply.clicked.connect(lambda : self.confirm_name())
        self.taskstep.task_step_check.clicked.connect(lambda : self.toggle_complete())

    def confirm_name(self):
        self.name = self.taskstep.lineEdit.text()

        self.taskstep.stackedWidget.setCurrentIndex(0)
        self.taskstep.task_step_label.setText(self.name)

    def toggle_complete(self):
        self.completed = not self.completed

        if self.completed:
            self.taskstep.task_step_check.setIcon(QIcon('icons_white/circle-check-big.svg'))
        else:
            self.taskstep.task_step_check.setIcon(QIcon('icons_white/circle.svg'))

        #print(tasks)

        tasks[cur_task]['taskSteps'][self] = self.completed

        #progress = ( sum(tasks[cur_task]['taskSteps'].values) // len(tasks[cur_task]['taskSteps']) ) * 100
        progress = (sum(tasks[cur_task]['taskSteps'].values()) / len(tasks[cur_task]['taskSteps'])) * 100
        tasks[cur_task]['progress'] = round(progress, 1)
        mw.task_step_progress.setValue(tasks[cur_task]['progress'])
        #print(tasks)
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
        self.task.task_check_4.clicked.connect(complete_task)
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

    if len(tasks[cur_task]['taskSteps']) == 0:
        mw.task_step_progress.setVisible(False)
        mw.task_step_progress.setValue(0)
    else:
        mw.task_step_progress.setValue(tasks[cur_task]['progress'])
        mw.task_step_progress.setVisible(True)

    if tasks[cur_task]['Completed']:
        mw.pushButton.setIcon(QIcon('icons_white/circle-check-big.svg'))
    else:
        mw.pushButton.setIcon(QIcon('icons_white/circle.svg'))

    mw.steps_label.setText(f'{task_name} steps')

    if tasks[task_name]['taskNo'] not in range(mw.stackedWidget_2.count()):
        task_step_page = QWidget()
        task_step_page_layout = QVBoxLayout(task_step_page)
        tasks[task_name]['taskStepsPage'] = task_step_page

        mw.stackedWidget_2.addWidget(task_step_page)

    mw.stackedWidget_2.setCurrentIndex(tasks[task_name]['taskNo'])
    print(tasks[task_name]['taskNo'],'<==>', mw.stackedWidget_2.currentIndex(), '/', mw.stackedWidget_2.count()-1)

def set_repeatable_menu():
    global popup
    popup.repeatable_widget.setVisible(popup.repeatable_toggle._checked)

def submit():
    global popup, task_ammo
    _task_name = popup.name_edit.text()
    if _task_name == '':
        _task_name = f"Task #{task_ammo}"

    _task_description = popup.description_edit.toPlainText()
    _task_due = str(popup.timeEdit.time())
    _task_difficulty = popup.diff_box.currentText()
    _task_category= popup.difficulty_combobox.currentText() # rename it pls

    #change user
    start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    end_time = datetime.datetime.now().strftime('%Y-%m-%d') + _task_due #change with adding repeatable

    cursor.execute("""
    INSERT INTO users
    (user, taskName, start_time, end_time, difficulty, category, completed, repeatable,next_occurrence,task_steps)
    VALUES (?,?,?,?,?,?,?,?,?)""",
    ('Yasinets',_task_name,start_time,end_time,_task_difficulty,_task_category,0,popup.repeatable_toggle._checked,0,''))
    conn.commit() #<-----------IMPORTANT (off for test cases)

    task = Task(_task_name, _task_description, _task_difficulty, _task_category, popup.repeatable_toggle._checked,parent=mw.tasks_scrollwidget)
    tasks[_task_name] = {'taskWidget': task, 'taskNo': task_ammo, 'taskSteps': {}, 'taskStepsPage': None, 'Completed':False}
    set_task_info(_task_name, _task_description, _task_difficulty, _task_category)




    task_ammo+=1


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
    global mw

    #mw.stackedWidget_2.setVisible(True)
    mw.task_step_progress.setVisible(True)

    task_page = tasks[cur_task]['taskStepsPage']
    task_page_layout = task_page.layout()
    task_step = TaskStep(parent=task_page)
    task_page_layout.addWidget(task_step.taskstep)

    tasks[cur_task]['taskSteps'][task_step] = False

    progress = (sum(tasks[cur_task]['taskSteps'].values()) / len(tasks[cur_task]['taskSteps'])) * 100
    tasks[cur_task]['progress'] = round(progress, 1)
    mw.task_step_progress.setValue(tasks[cur_task]['progress'])
    #tasks[cur_task]['progress'] = 0
def complete_task():
    global mw
    tasks[cur_task]['Completed'] = not tasks[cur_task]['Completed']

    if tasks[cur_task]['Completed']:
        mw.pushButton.setIcon(QIcon('icons_white/circle-check-big.svg'))
        tasks[cur_task]['taskWidget'].task.task_check_4.setIcon(QIcon('icons_white/circle-check-big.svg'))
    else:
        mw.pushButton.setIcon(QIcon('icons_white/circle.svg'))
        tasks[cur_task]['taskWidget'].task.task_check_4.setIcon(QIcon('icons_white/circle.svg'))

conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

loader = QUiLoader()

app = QApplication(sys.argv)
mw = loader.load(main_ui, None)

mw.task_step_progress.setVisible(False)
#mw.stackedWidget_2.setVisible(False)
mw.stackedWidget.setVisible(False)
mw.tabWidget.setCurrentIndex(0)

mw.add_task_button.clicked.connect(show_add_task_popup)
mw.add_task_step_button.clicked.connect(add_task_step)
mw.pushButton.clicked.connect(complete_task)
mw.show()
app.exec()