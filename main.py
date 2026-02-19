import sqlite3
import sys
import datetime

from PySide6.QtGui import QIcon, Qt
from PySide6.QtCore import QEvent, QDate, QDateTime
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QAbstractScrollArea

from logic import AnimatedToggle

#moveit to .env
user = 'Yasinets'

mounth_number = {
'January' : 1,
'February' : 2,
'March' : 3,
'April' : 4,
'May' : 5,
'June' : 6,
'July' : 7,
'August' : 8,
'September' : 9,
'October' : 10,
'November' : 11,
'December' : 12,
}
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
'light-gray' : 'rgb(65, 65, 65)',
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

cur_task = None
task_ammo = 0
tasks = {}

mw = popup = None
task_widget_ui = "task_v4.ui"
main_ui = "v25.ui"
popup_ui = "add_task_popup_v6.ui"
task_step_ui = 'task_step_v3.ui'

loader = QUiLoader()

conn = sqlite3.connect('../db/user_data.db')
cursor = conn.cursor()

class TaskStep(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        global mw

        self.taskstep = loader.load(task_step_ui, self)
        self.completed = False
        self.taskstep.stackedWidget.setCurrentIndex(1)
        self.taskstep.stackedWidget.setStyleSheet(f"""background-color: {palette['black']};""")

        self.taskstep.task_step_apply.clicked.connect(lambda : self.confirm_name())
        self.taskstep.task_step_check.clicked.connect(lambda : self.toggle_complete())
        self.taskstep.task_step_edit.clicked.connect(lambda : self.edit_name())
        self.taskstep.task_step_delete.clicked.connect(lambda : self.deconstruct())

    def confirm_name(self):
        self.name = self.taskstep.lineEdit.text()

        self.taskstep.stackedWidget.setCurrentIndex(0)
        self.taskstep.task_step_label.setText(self.name)

    def toggle_complete(self):
        self.completed = not self.completed

        if self.completed:
            self.taskstep.task_step_check.setIcon(QIcon('../sources/icons_white/circle-check-big.svg'))
        else:
            self.taskstep.task_step_check.setIcon(QIcon('../sources/icons_white/circle.svg'))

        tasks[cur_task]['taskSteps']['steps'][self] = self.completed

        update_progress_bar()

    def edit_name(self):
        self.taskstep.stackedWidget.setCurrentIndex(1)

    def deconstruct(self):
        self.taskstep.deleteLater()
        del tasks[cur_task]['taskSteps']['steps'][self]

        update_progress_bar()
        del self

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
        self.task.task_name.setText(name)

        self.start_time = convert_qtTime_str(popup.at_timeedit.time())
        self.end_time  = convert_qtTime_str(popup.due_timeedit.time())

        self.task.task_duration.setText(f'{datetime.datetime.fromtimestamp(self.start_time).strftime("%H:%M")} - {datetime.datetime.fromtimestamp(self.end_time).strftime("%H:%M")}')
        self.task.categ_icon.setIcon(QIcon(f"sources/icons_white/{icons[category]}"))
        bg_color = palette[diff_col[difficulty]]
        self.task.setStyleSheet(f"""background-color: {bg_color}; border-radius: 20px;""")

        self.task.setMouseTracking(True)
        self.task.setAttribute(Qt.WA_StyledBackground, True)


        self.task.installEventFilter(self)
        self.task.task_check.clicked.connect(lambda x: complete_task(self.name))
        parent.layout().addWidget(self.task)

    def update_duration(self):
        self.task.task_duration.setText(f'{datetime.datetime.fromtimestamp(self.start_time).strftime("%H:%M")} - {datetime.datetime.fromtimestamp(self.end_time).strftime("%H:%M")}')


    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            set_task_info(self.name, self.description, self.difficulty, self.category)

    def deconstruct(self):
        mw.tasks_scrollwidget.layout().removeWidget(self.task)
        self.task.setParent(None)
        self.task.deleteLater()
        del tasks[cur_task]

        #update_progress_bar()
        mw.task_info_stack.setCurrentWidget(mw.empty_page)
        mw.task_info_stack.setVisible(False)
        #print(mw.task_info_stack.)

        del self

def set_task_info(task_name, task_description, task_difficulty, task_category):
    global mw, cur_task

    cur_task = task_name


    mw.task_info_stack.setVisible(True)

    mw.task_info_stack.setCurrentIndex(0)
    mw.category_stack.setCurrentIndex(0)
    mw.difficulty_stack.setCurrentIndex(0)
    mw.description_label_edit_layout.setCurrentIndex(0)

    mw.task_name_label.setText(task_name)
    mw.category.setText(task_category)
    mw.difficulty.setText(task_difficulty)  # RENAME THEIR LABELS
    mw.description_input_label.setText(task_description)

    mw.at_timeedit.setTime(tasks[cur_task]['duration'][0])
    mw.due_timeedit.setTime(tasks[cur_task]['duration'][1])

    if tasks[cur_task]['repeatable']['is_repeatable']:
        mw.repeatable_set_widget.setVisible(True)
        if not mw.repeatable_toggle._checked:
            mw.repeatable_toggle.on_click()

        mw.task_graphs_widget.setVisible(True)

        next_occurrence_date =  datetime.datetime.fromtimestamp(tasks[cur_task]['repeatable']['next_occurrence']).strftime("%d.%m.%Y")
        next_occurrence_time =  datetime.datetime.fromtimestamp(tasks[cur_task]['repeatable']['next_occurrence']).strftime("%H:%M")

        mw.next_time_label.setText(f'Next time you will recieve this task on {next_occurrence_date} at {next_occurrence_time}')

        mw.every_box.setCurrentIndex(tasks[cur_task]['repeatable']['rep_option'])
        set_mw_every_stack(tasks[cur_task]['repeatable']['rep_vals'])
    else:
        if mw.repeatable_toggle._checked:
            mw.repeatable_toggle.on_click()

        mw.repeatable_set_widget.setVisible(False)
        mw.task_graphs_widget.setVisible(False)

    if len(tasks[cur_task]['taskSteps']['steps']) == 0:
        mw.task_step_progress.setVisible(False)
        mw.task_step_progress.setValue(0)
    else:
        update_progress_bar()
        mw.task_step_progress.setVisible(True)

    if tasks[cur_task]['completed']:
        mw.task_complete_button.setIcon(QIcon('../sources/icons_white/circle-check-big.svg'))
    else:
        mw.task_complete_button.setIcon(QIcon('../sources/icons_white/circle.svg'))

    if tasks[task_name]['taskNo'] not in range(mw.steps_stack.count()):
        task_step_page = QWidget()
        task_step_page_layout = QVBoxLayout(task_step_page)
        tasks[task_name]['taskSteps']['page'] = task_step_page

        mw.steps_stack.addWidget(task_step_page)

    mw.steps_label.setText(f'{task_name} steps')
    mw.steps_stack.setCurrentIndex(tasks[task_name]['taskNo'])


    #for i in range(mw.steps_stack.currentWidget().layout().count()):
    #    item = mw.steps_stack.currentWidget().layout().itemAt(i)
#
    #    print(item.geometry().width(), item.geometry().height())

    mw.steps_stack.setMaximumHeight(mw.steps_stack.currentWidget().layout().sizeHint().height())
    mw.steps_stack.updateGeometry()

def set_popup_repeatable_menu():
    global popup
    popup.repeatable_widget.setVisible(popup.repeatable_toggle._checked)

def toggle_mw_repeatable_menu():#On task createon after editing repeatable on prev task
                                # raises console Error that cur_task = ''
                                # but everything works so idk what is it
    global mw
    status = mw.repeatable_toggle._checked
    mw.repeatable_set_widget.setVisible(status)
    tasks[cur_task]['repeatable']['is_repeatable'] = status

def convert_qtTime_str(qt_Time):
    cur_date = QDate.currentDate()
    time = QDateTime(cur_date, qt_Time).toSecsSinceEpoch()

    return time

def submit():
    global popup, task_ammo, cur_task

    _task_name = popup.name_edit.text()
    cur_task = _task_name
    _task_repeatable = popup.repeatable_toggle._checked
    if _task_name == '':
        _task_name = f"Task #{task_ammo}"

    _task_description = popup.description_edit.toPlainText()
    _task_difficulty = popup.diff_box.currentText()
    _task_category= popup.difficulty_combobox.currentText() # rename it pls

    start_time = convert_qtTime_str(popup.at_timeedit.time())
    end_time = convert_qtTime_str(popup.due_timeedit.time())

    cur_time_in = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    next_occurrence = rep_option = rep_vals = None
    if _task_repeatable:
        mw.repeatable_set_widget.setVisible(True)

        rep_option = popup.every_box.currentIndex()
        next_occurrence, rep_vals = (calculate_next_occurrence(
            popup.every_box.currentText(),
            popup.at_timeedit.time(),
            popup
        ))
        mw.every_box.setCurrentIndex(popup.every_box.currentIndex())
        set_mw_every_stack()
    else:
        if mw.repeatable_toggle._checked:
            mw.repeatable_toggle.on_click()
        mw.repeatable_set_widget.setVisible(False)

    cursor.execute("""
    INSERT INTO users
    (user, taskName, start_time, end_time, difficulty, category, completed, repeatable,next_occurrence,task_steps)
    VALUES (?,?,?,?,?,?,?,?,?,?)""",
    (user,_task_name,start_time,end_time,_task_difficulty,_task_category,0,_task_repeatable,next_occurrence,''))
    conn.commit() #<-----------IMPORTANT (off for test cases)

    task = Task(_task_name, _task_description, _task_difficulty, _task_category, _task_repeatable,parent=mw.tasks_scrollwidget)
    tasks[_task_name] = {'taskWidget': task,
                         'taskNo': task_ammo,
                         'completed':False,
                         'duration':[popup.at_timeedit.time(), popup.due_timeedit.time()],
                         'taskSteps': {
                             'steps' : {},
                             'page' : None
                         },
                         'repeatable': {
                             'is_repeatable' : _task_repeatable,
                             'next_occurrence': next_occurrence,
                             'rep_option' : rep_option,
                             'rep_vals' : rep_vals
                         }
                         }

    set_task_info(_task_name, _task_description, _task_difficulty, _task_category)

    task_ammo+=1

    popup.close()

    #add repeatable

def show_add_task_popup():
    global popup
    popup = None
    popup = loader.load(popup_ui, None)

    #popup.setStretch(1,1,1,1,1,1,1,1)

    popup.repeatable_widget.setVisible(False)
    popup.every_stack.setCurrentWidget(popup.day)
    popup.every_stack.setVisible(False)

    popup.repeatable_toggle = AnimatedToggle.AnimatedToggle(popup)
    popup.repeatable_layout.replaceWidget(popup.rep_switch, popup.repeatable_toggle)
    popup.repeatable_toggle.toggled.connect(set_popup_repeatable_menu)

    popup.submit_button.clicked.connect(submit)

    popup.every_box.currentTextChanged.connect(set_popup_every_stack)

    popup.show()

def set_popup_every_stack():
    global popup
    cur_option = popup.every_box.currentText()

    popup.every_stack.setVisible(True)
    if cur_option == 'Few Days':
        popup.every_stack.setCurrentWidget(popup.few_days)

    elif cur_option == 'Week':
        popup.every_stack.setCurrentWidget(popup.week)

    elif cur_option == 'Mounth':
        popup.every_stack.setCurrentWidget(popup.mounth)

    elif cur_option == 'Year':
        popup.every_stack.setCurrentWidget(popup.year)

    elif cur_option == 'Day':
        popup.every_stack.setCurrentWidget(mw.day)
        popup.every_stack.setVisible(False)

def set_mw_every_stack(vals = None):
    cur_option = mw.every_box.currentText()

    mw.every_stack.setVisible(True)
    if cur_option == 'Few Days':
        mw.every_stack.setCurrentWidget(mw.few_days)

        if vals:
            mw.few_days_edit.setText(str(vals[0]))
        else:
            mw.few_days_edit.setText(popup.few_days_edit.text())

    elif cur_option == 'Week':
        mw.every_stack.setCurrentWidget(mw.week)
        if vals:
            pass
        else:
            pass
        # to do

    elif cur_option == 'Mounth':
        mw.every_stack.setCurrentWidget(mw.mounth)

        if vals:
            mw.day_edit_2.setText(str(vals[0]))
        else:
            mw.day_edit_2.setText(popup.day_edit_2.text())

    elif cur_option == 'Year':
        mw.every_stack.setCurrentWidget(mw.year)

        if vals:
            mw.day_edit.setText(str(vals[0]))
            mw.mounth_edit.setCurrentText(vals[1])
        else:
            mw.day_edit.setText(popup.day_edit.text())
            mw.mounth_edit.setCurrentIndex(popup.mounth_edit.currentIndex())

    elif cur_option == 'Day':
        mw.every_stack.setCurrentWidget(mw.day)
        mw.every_stack.setVisible(False)

def add_task_step():
    #mw.steps_stack.setVisible(True)
    mw.task_step_progress.setVisible(True)

    task_page = tasks[cur_task]['taskSteps']['page']
    task_page_layout = task_page.layout()
    task_step = TaskStep(parent=task_page)
    task_page_layout.addWidget(task_step.taskstep)

    tasks[cur_task]['taskSteps']['steps'][task_step] = False

    update_progress_bar()

    mw.steps_stack.setMaximumHeight(mw.steps_stack.currentWidget().layout().sizeHint().height() + 90)
    mw.steps_stack.updateGeometry()

    #tasks[cur_task]['progress'] = 0

def calculate_next_occurrence(rep_type, at_time, caller):
    cur_date = QDate.currentDate()
    rep_vals = []

    if rep_type == 'Few Days':

        cur_datetime_stamp = QDateTime(cur_date, at_time).toSecsSinceEpoch()

        value = int(caller.few_days_edit.text())
        rep_vals.append(value)

        next_occurrence = cur_datetime_stamp + 86400 * value

    elif rep_type == 'Week':
        return 0
        pass#gonnado later

    elif rep_type == 'Mounth':
        cur_mounth = QDate(cur_date.year(), cur_date.month(), 1)
        cur_mounth_stamp = QDateTime(cur_mounth, at_time).toSecsSinceEpoch()

        value = int(caller.day_edit_2.text())
        rep_vals.append(value)

        next_occurrence = cur_mounth_stamp + 86400 * (value-1)
    elif rep_type == 'Year':
        cur_year = QDate(cur_date.year(), 1, 1)
        cur_year_stamp = QDateTime(cur_year, at_time).toSecsSinceEpoch()

        day_value = int(caller.day_edit.text())
        mounth_value = mounth_number[caller.mounth_edit.currentText()]

        rep_vals.append(day_value)
        rep_vals.append(caller.mounth_edit.currentText())

        req_date = QDate(cur_date.year()+1, mounth_value, day_value)

        next_occurrence = cur_year_stamp + 86400 * cur_year.daysTo(req_date)

    elif rep_type == 'Day':
        cur_datetime = QDateTime(cur_date, at_time).toSecsSinceEpoch()
        next_occurrence = cur_datetime + 86400

    return next_occurrence, rep_vals

def update_progress_bar():
    global mw
    if cur_task in tasks and len(tasks[cur_task]['taskSteps']['steps']) != 0:
        progress = (sum(tasks[cur_task]['taskSteps']['steps'].values()) / len(tasks[cur_task]['taskSteps']['steps'])) * 100
        tasks[cur_task]['progress'] = round(progress, 1)
        tasks[cur_task]['taskWidget'].task.task_progress.setValue(round(progress, 1))

    else:
        progress = 0

    mw.task_step_progress.setValue(round(progress, 1))

def complete_task(task_name = cur_task):
    global mw

    if task_name == cur_task:
        tasks[cur_task]['completed'] = not tasks[cur_task]['completed']
        if tasks[cur_task]['completed']:
            mw.task_complete_button.setIcon(QIcon('../sources/icons_white/circle-check-big.svg'))
            tasks[cur_task]['taskWidget'].task.task_check.setIcon(QIcon('../sources/icons_white/circle-check-big.svg'))
        else:
            mw.task_complete_button.setIcon(QIcon('../sources/icons_white/circle.svg'))
            tasks[cur_task]['taskWidget'].task.task_check.setIcon(QIcon('../sources/icons_white/circle.svg'))

    else:
        tasks[task_name]['completed'] = not tasks[task_name]['completed']
        if tasks[task_name]['completed']:
            tasks[task_name]['taskWidget'].task.task_check.setIcon(QIcon('../sources/icons_white/circle-check-big.svg'))
        else:
            tasks[task_name]['taskWidget'].task.task_check.setIcon(QIcon('../sources/icons_white/circle.svg'))

def edit_repeatable():
    global mw
    if mw.edit_repeatable_button.mode == 'edit':
        mw.edit_repeatable_button.mode = 'apply'
        mw.edit_repeatable_button.setIcon(QIcon('../sources/icons_white/check.svg'))

        mw.repeatable_edit_info_widget.setEnabled(True)
    elif mw.edit_repeatable_button.mode == 'apply':
        mw.edit_repeatable_button.mode = 'edit'
        mw.edit_repeatable_button.setIcon(QIcon('../sources/icons_white/pencil.svg'))

        rep_option = mw.every_box.currentIndex()
        next_occurrence, rep_vals = (calculate_next_occurrence(
            mw.every_box.currentText(),
            mw.at_timeedit.time(),
            mw
        ))

        tasks[cur_task]['repeatable']['rep_option'] = rep_option
        tasks[cur_task]['repeatable']['rep_vals'] = rep_vals
        tasks[cur_task]['repeatable']['next_occurrence'] = next_occurrence

        next_occurrence_date = datetime.datetime.fromtimestamp(next_occurrence).strftime("%d.%m.%Y")
        next_occurrence_time = datetime.datetime.fromtimestamp(next_occurrence).strftime("%H:%M")

        mw.next_time_label.setText(f'Next time you will recieve this task on {next_occurrence_date} at {next_occurrence_time}')
        mw.repeatable_edit_info_widget.setEnabled(False)

def edit_starttime():
    global mw, cur_task
    prev = tasks[cur_task]['duration'][0]

    tasks[cur_task]['duration'][0] = mw.at_timeedit.time()

    difference = prev.secsTo(mw.at_timeedit.time())

    tasks[cur_task]['repeatable']['next_occurrence'] += difference

    next_occurrence_date = datetime.datetime.fromtimestamp(tasks[cur_task]['repeatable']['next_occurrence']).strftime("%d.%m.%Y")
    next_occurrence_time = datetime.datetime.fromtimestamp(tasks[cur_task]['repeatable']['next_occurrence']).strftime("%H:%M")

    mw.next_time_label.setText(f'Next time you will recieve this task on {next_occurrence_date} at {next_occurrence_time}')

    cur_task_widget = tasks[cur_task]['taskWidget']
    cur_task_widget.start_time = convert_qtTime_str(mw.at_timeedit.time())
    cur_task_widget.update_duration()

def edit_endtime():
    global mw, cur_task
    tasks[cur_task]['duration'][1] = mw.due_timeedit.time()

    cur_task_widget = tasks[cur_task]['taskWidget']
    cur_task_widget.end_time = convert_qtTime_str(mw.due_timeedit.time())
    cur_task_widget.update_duration()

def main():

    app = QApplication(sys.argv)
    mw = loader.load(main_ui, None)

    mw.task_info_scroll_area.setWidgetResizable(True)
    mw.task_info_scroll_area.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    mw.task_step_progress.setVisible(False)
    mw.task_info_stack.setVisible(False)
    mw.tabWidget.setCurrentIndex(0)

    mw.repeatable_toggle = AnimatedToggle.AnimatedToggle(mw)
    mw.repeatable_widget.layout().replaceWidget(mw.rep_switch, mw.repeatable_toggle)

    mw.repeatable_toggle.toggled.connect(toggle_mw_repeatable_menu)
    mw.add_task_button.clicked.connect(show_add_task_popup)
    mw.add_task_step_button.clicked.connect(add_task_step)
    mw.task_complete_button.clicked.connect(lambda x: complete_task(cur_task))
    mw.every_box.currentTextChanged.connect(set_mw_every_stack)
    mw.delete_task.clicked.connect(lambda x: tasks[cur_task]['taskWidget'].deconstruct())
    mw.edit_repeatable_button.mode = 'edit'
    mw.edit_repeatable_button.clicked.connect(edit_repeatable)
    mw.at_timeedit.timeChanged.connect(lambda x: edit_starttime())
    mw.due_timeedit.timeChanged.connect(lambda x: edit_endtime())


    mw.show()
    app.exec()