import datetime
from traceback import print_tb

from PySide6.QtCore import QDateTime, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtUiTools import QUiLoader

#variables
from config.env_loader import main_ui, user
from data.init_db import cursor, conn
from logic.appState import state

#funcs
from logic.core import convert_qtTime_int, calculate_next_occurrence, datetime_str, convert_qtTime_int, \
    calculate_next_occurrence_raw
from logic.signalHub import signals

#instances
from logic.widgets import TaskStep, Task

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = QUiLoader().load(main_ui, None)
        self.funcs = MWindowFuncs(ui=self.ui)

        self.setStart()
        self.setCustomWidgets()
        self.loadTasks()
        self.linkFuncs()
        #self.ui.show())

    def setStart(self):
        self.ui.task_step_progress.setVisible(False)
        self.ui.task_info_stack.setVisible(False)

        # self.ui.tabWidget.setCurrentIndex(0)

    def setCustomWidgets(self):
        from logic.widgets import  AnimatedToggle
        self.ui.repeatable_toggle = AnimatedToggle(self.ui)
        self.ui.repeatable_widget.layout().replaceWidget(self.ui.rep_switch, self.ui.repeatable_toggle)

    def linkFuncs(self):
        #signals
        signals.complete_task.connect(lambda name: self.funcs.complete_task(task_name=name))
        signals.update_task_info.connect(lambda taksId: self.funcs.set_task_info(taksId))
        signals.update_progress_bar.connect(lambda: self.funcs.update_progress_bar())
        signals.setEmptyPage.connect(lambda name: self.funcs.setEmptyPage(name=name))
        #popup related
        self.ui.add_task_button.clicked.connect(lambda x: signals.show_add_task_popup.emit())

        #taskstep related
        self.ui.add_task_step_button.clicked.connect(lambda x: self.funcs.add_task_step())

        #task related
        self.ui.delete_task.clicked.connect(lambda x: state.tasks[state.cur_task]['taskWidget'].deconstruct())
        self.ui.every_box.currentTextChanged.connect(lambda x: self.funcs.set_mw_every_stack(state.tasks[state.cur_task]['repeatable']['rep_vals']) )
        self.ui.repeatable_toggle.toggled.connect(lambda x: self.funcs.toggle_mw_repeatable_menu())
        self.ui.task_complete_button.clicked.connect(lambda x: self.funcs.complete_task(state.cur_task))
        self.ui.edit_repeatable_button.mode = 'edit'
        self.ui.edit_repeatable_button.clicked.connect(lambda x: self.funcs.edit_repeatable())
        self.ui.at_timeedit.timeChanged.connect(lambda x: self.funcs.edit_starttime())
        self.ui.due_timeedit.timeChanged.connect(lambda x: self.funcs.edit_endtime())
        self.ui.tasks_prev_button.clicked.connect(lambda x: self.funcs.change_date(-1))
        self.ui.tasks_next_button.clicked.connect(lambda x: self.funcs.change_date(1))


    def loadTasks(self):
        ### task widget setting
        cur_date = datetime_str(state.cur_date)

        cursor.execute('''
                SELECT 
                    taskName,                   
                    date,                   
                    at_time,                    
                    due_time,                   
                    difficulty,                 
                    category,                   
                    completed,                  
                    repeatable,                 
                    rep_option,                 
                    rep_vals,                   
                    task_steps_infos,
                    description,
                    id              
                FROM users WHERE user=? AND date=?''' , (user,cur_date))

        data = cursor.fetchall()

        date_page = QWidget()
        date_page.setObjectName(cur_date)
        date_page_layout = QVBoxLayout(date_page)
        self.ui.task_list_stack.addWidget(date_page)
        self.ui.task_list_stack.setCurrentWidget(date_page)
        state.dates.append(cur_date)
        #


        if data:
            for task in data:
                name = task[0]
                date = task[1]
                startTime = task[2]
                endTime = task[3]
                difficulty = task[4]
                category = task[5]
                completed = task[6]
                is_repeatable = task[7]
                rep_option = task[8]
                rep_vals = task[9].split(' ')
                taskSteps = task[10]
                description = task[11]
                taskId = task[12]

                state.cur_task = taskId

                print(startTime, endTime)
                state.tasks[taskId] = {
                    'taskName': name,
                    'taskNo' : state.task_ammo,
                    'taskWidget': None,
                    'difficulty': difficulty,
                    'category': category,
                    'description': description,
                    'completed': completed,
                    'duration': [startTime, endTime],
                    'taskDate': {
                        'date': date,
                        'page': None
                    },
                    'taskSteps': {
                        'steps': {},
                        'page': None
                    },
                    'repeatable': {
                        'is_repeatable': is_repeatable,
                        'next_occurrence': None,  # calculate_next_occur
                        'rep_option': rep_option,
                        'rep_vals': rep_vals
                    }
                }
                task_widget = Task(taskId, name, description, difficulty, category, startTime, endTime,
                                   parent=None)  # change it
                state.tasks[taskId]['taskWidget'] = task_widget

                if len(taskSteps) > 0 or True: #change it
                    task_step_page = QWidget()
                    task_step_page_layout = QVBoxLayout(task_step_page)
                    state.tasks[taskId]['taskSteps']['page'] = task_step_page

                    self.ui.steps_stack.addWidget(task_step_page)
                    self.ui.task_step_progress.setVisible(True)
                    print('lf', state.tasks[taskId]['taskSteps']['page'])

                    for step in taskSteps.split('@@')[:-1]:

                        step_name, step_completed = step[:-1], int(step[-1])
                        state.tasks[taskId]['taskSteps']['steps'][step_name] = step_completed

                        # mw.steps_stack.setVisible(True)

                        #task_page = state.tasks[state.cur_task]['taskSteps']['page']
                        task_page_layout = task_step_page.layout()
                        task_step = TaskStep(step_name, parent=task_step_page)
                        task_page_layout.addWidget(task_step.taskstep)

                        state.tasks[state.cur_task]['taskSteps']['steps'][step_name] = step_completed

                        self.funcs.update_progress_bar()

                        self.ui.steps_stack.setMaximumHeight(
                            self.ui.steps_stack.currentWidget().layout().sizeHint().height() + 90)
                        self.ui.steps_stack.updateGeometry()

                if is_repeatable:
                    next_occurrence = calculate_next_occurrence_raw(
                        rep_option,
                        rep_vals,
                        startTime)


                    state.tasks[taskId]['repeatable']['next_occurrence'] = next_occurrence

                    next_occurrence_date = datetime.datetime.fromtimestamp(next_occurrence).strftime("%d.%m.%Y")
                    next_occurrence_time = datetime.datetime.fromtimestamp(next_occurrence).strftime("%H:%M")
                    print('HEEEEEEEEEEEEEEY', rep_vals, rep_option, next_occurrence_date)
                    self.ui.next_time_label.setText(f'Next time you will recieve this task on {next_occurrence_date} at {next_occurrence_time}')
                    self.ui.every_box.setCurrentIndex(state.tasks[state.cur_task]['repeatable']['rep_option'])
                    self.funcs.set_mw_every_stack(state.tasks[state.cur_task]['repeatable']['rep_vals'])


                state.tasks[taskId]['taskDate']['page'] = date_page
                date_page.layout().addWidget(state.tasks[taskId]['taskWidget'].task)

                state.task_ammo += 1

                self.funcs.check_completion()
                state.print_tasks()

class MWindowFuncs():
    def __init__(self, ui):
        self.ui = ui

    def set_task_info(self, taskId):
        ### variables
        state.cur_task = taskId
        task_date = state.tasks[taskId]['taskDate']['date']
        task_name = state.tasks[taskId]['taskName']
        task_no = state.tasks[taskId]['taskNo']
        #task_duration = state.tasks[state.cur_task]['duration'][0]

        at_time = QDateTime.fromSecsSinceEpoch(state.tasks[state.cur_task]['duration'][0], Qt.UTC).time()
        due_time = QDateTime.fromSecsSinceEpoch(state.tasks[state.cur_task]['duration'][0], Qt.UTC).time()

        ### visibility
        self.ui.task_info_stack.setVisible(True)

        self.ui.task_info_stack.setCurrentIndex(0)
        self.ui.category_stack.setCurrentIndex(0)
        self.ui.difficulty_stack.setCurrentIndex(0)
        self.ui.description_label_edit_layout.setCurrentIndex(0)
        ### value assigment
        self.ui.task_name_label.setText(task_name)
        self.ui.category.setText(state.tasks[taskId]['category'])
        self.ui.difficulty.setText(state.tasks[taskId]['difficulty'])  # RENAME THEIR LABELS
        self.ui.description_input_label.setText(state.tasks[taskId]['description'])
        self.ui.at_timeedit.setTime(at_time)
        self.ui.due_timeedit.setTime(due_time)

        self.check_completion()
        ### repeatable repeatable setting
        if state.tasks[state.cur_task]['repeatable']['is_repeatable']:
            self.ui.repeatable_set_widget.setVisible(True)
            if not self.ui.repeatable_toggle._checked:
                self.ui.repeatable_toggle.on_click()

            self.ui.task_graphs_widget.setVisible(True)

            next_occurrence_date =  datetime.datetime.fromtimestamp(state.tasks[state.cur_task]['repeatable']['next_occurrence']).strftime("%d.%m.%Y")
            next_occurrence_time =  datetime.datetime.fromtimestamp(state.tasks[state.cur_task]['repeatable']['next_occurrence']).strftime("%H:%M")

            self.ui.next_time_label.setText(f'Next time you will recieve this task on {next_occurrence_date} at {next_occurrence_time}')

            self.ui.every_box.setCurrentIndex(state.tasks[state.cur_task]['repeatable']['rep_option'])
            self.set_mw_every_stack(state.tasks[state.cur_task]['repeatable']['rep_vals'])
        else:
            if self.ui.repeatable_toggle._checked:
                self.ui.repeatable_toggle.on_click()

            self.ui.repeatable_set_widget.setVisible(False)
            self.ui.task_graphs_widget.setVisible(False)
        ### step widget visibility
        if len(state.tasks[state.cur_task]['taskSteps']['steps']) == 0:
            self.ui.task_step_progress.setVisible(False)
            self.ui.task_step_progress.setValue(0)
        else:
            self.update_progress_bar()
            self.ui.task_step_progress.setVisible(True)
        ### completed setting
        if state.tasks[state.cur_task]['completed']:
            self.ui.task_complete_button.setIcon(QIcon('sources/icons_white/circle-check-big.svg'))
        else:
            self.ui.task_complete_button.setIcon(QIcon('sources/icons_white/circle.svg'))
        ### steps stting
        if task_no not in range(self.ui.steps_stack.count()):
            print('hey hey1')
            task_step_page = QWidget()
            task_step_page_layout = QVBoxLayout(task_step_page)
            state.tasks[taskId]['taskSteps']['page'] = task_step_page

            self.ui.steps_stack.addWidget(task_step_page)

        self.ui.steps_label.setText(f'{task_name} steps')
        self.ui.steps_stack.setCurrentIndex(task_no)

        self.ui.steps_stack.setMaximumHeight(self.ui.steps_stack.currentWidget().layout().sizeHint().height())
        self.ui.steps_stack.updateGeometry()
#       ### date setting
        self.ui.tasks_date_label.setText(task_date)

        if task_date not in state.dates:

            date_page = QWidget()
            date_page.setObjectName(task_date)
            date_page_layout = QVBoxLayout(date_page)

            self.ui.task_list_stack.addWidget(date_page)
            state.dates.append(task_date)

        else:
            date_page = self.ui.task_list_stack.findChild(QWidget, task_date)
#
        state.tasks[taskId]['taskDate']['page'] = date_page
        date_page.layout().addWidget(state.tasks[taskId]['taskWidget'].task)
        self.ui.task_list_stack.setCurrentWidget(date_page)
#       ###
    def edit_starttime(self):
        if state.cur_task is None:
            return

        at_time = self.ui.at_timeedit.time()
        due_time = state.tasks[state.cur_task]['duration'][1]

        prev = state.tasks[state.cur_task]['duration'][0]
        cur_task_widget = state.tasks[state.cur_task]['taskWidget']

        at_time_converted = convert_qtTime_int(at_time)
        state.tasks[state.cur_task]['duration'][0] = at_time_converted

        cur_task_widget.start_time = at_time_converted

        cursor.execute('''UPDATE users SET at_time=? WHERE user=? AND id=?''', (at_time_converted, user, state.cur_task))

        if at_time_converted > due_time:
            state.tasks[state.cur_task]['duration'][1] = convert_qtTime_int(at_time)
            cur_task_widget.end_time = convert_qtTime_int(at_time)

            cursor.execute('''UPDATE users SET due_time=? WHERE user=? AND id=?''',
                           (at_time_converted, user, state.cur_task))

            self.ui.due_timeedit.setTime(at_time)
        cur_task_widget.update_duration()
        conn.commit()
        if state.tasks[state.cur_task]['repeatable']['next_occurrence'] is not None:
            difference = prev - convert_qtTime_int(at_time)

            state.tasks[state.cur_task]['repeatable']['next_occurrence'] += difference

            next_occurrence_date = datetime.datetime.fromtimestamp(state.tasks[state.cur_task]['repeatable']['next_occurrence']).strftime("%d.%m.%Y")
            next_occurrence_time = datetime.datetime.fromtimestamp(state.tasks[state.cur_task]['repeatable']['next_occurrence']).strftime("%H:%M")

            self.ui.next_time_label.setText(f'Next time you will recieve this task on {next_occurrence_date} at {next_occurrence_time}')

    def edit_endtime(self):
        due_time = self.ui.due_timeedit.time()
        at_time = state.tasks[state.cur_task]['duration'][0]

        due_time_converted = convert_qtTime_int(due_time)
        state.tasks[state.cur_task]['duration'][1] = due_time_converted

        cursor.execute('''UPDATE users SET due_time=? WHERE user=? AND id=?''',
                       (due_time_converted, user, state.cur_task))

        cur_task_widget = state.tasks[state.cur_task]['taskWidget']
        cur_task_widget.end_time = due_time_converted
        print(state.tasks[state.cur_task]['duration'])
        print(due_time)

        if due_time_converted < at_time:
            state.tasks[state.cur_task]['duration'][0] = convert_qtTime_int(due_time)
            cur_task_widget.start_time = convert_qtTime_int(due_time)

            cursor.execute('''UPDATE users SET at_time=? WHERE user=? AND id=?''',
                           (due_time_converted, user, state.cur_task))
            self.ui.at_timeedit.setTime(due_time)

        cur_task_widget.update_duration()
        conn.commit()

    def toggle_mw_repeatable_menu(self):
        status = self.ui.repeatable_toggle._checked
        self.ui.repeatable_set_widget.setVisible(status)
        state.tasks[state.cur_task]['repeatable']['is_repeatable'] = status

        cursor.execute('''UPDATE users SET repeatable=? WHERE user=? AND id=?''',
                       (status, user, state.cur_task))
        conn.commit()

    def set_mw_every_stack(self, vals):
        cur_option = self.ui.every_box.currentText()

        self.ui.every_stack.setVisible(True)
        if cur_option == 'Few Days':
            self.ui.every_stack.setCurrentWidget(self.ui.few_days)

            self.ui.few_days_edit.setText(str(vals[0]))

        elif cur_option == 'Week':
            self.ui.every_stack.setCurrentWidget(self.ui.week)
            # to do

        elif cur_option == 'Mounth':
            self.ui.every_stack.setCurrentWidget(self.ui.mounth)

            self.ui.day_edit_2.setText(str(vals[0]))

        elif cur_option == 'Year':
            self.ui.every_stack.setCurrentWidget(self.ui.year)

            self.ui.day_edit.setText(str(vals[0]))
            self.ui.mounth_edit.setCurrentText(vals[1])

        elif cur_option == 'Day':
            self.ui.every_stack.setCurrentWidget(self.ui.day)
            self.ui.every_stack.setVisible(False)

    def edit_repeatable(self):
        if self.ui.edit_repeatable_button.mode == 'edit':
            self.ui.edit_repeatable_button.mode = 'apply'
            self.ui.edit_repeatable_button.setIcon(QIcon('sources/icons_white/check.svg'))

            self.ui.repeatable_edit_info_widget.setEnabled(True)
        elif self.ui.edit_repeatable_button.mode == 'apply':
            self.ui.edit_repeatable_button.mode = 'edit'
            self.ui.edit_repeatable_button.setIcon(QIcon('sources/icons_white/pencil.svg'))

            rep_option = self.ui.every_box.currentIndex()
            next_occurrence, rep_vals = (calculate_next_occurrence(
                self.ui.every_box.currentText(),
                self.ui.at_timeedit.time(),
                self
            ))

            state.tasks[state.cur_task]['repeatable']['rep_option'] = rep_option
            state.tasks[state.cur_task]['repeatable']['rep_vals'] = rep_vals
            state.tasks[state.cur_task]['repeatable']['next_occurrence'] = next_occurrence

            next_occurrence_date = datetime.datetime.fromtimestamp(next_occurrence).strftime("%d.%m.%Y")
            next_occurrence_time = datetime.datetime.fromtimestamp(next_occurrence).strftime("%H:%M")

            self.ui.next_time_label.setText(f'Next time you will recieve this task on {next_occurrence_date} at {next_occurrence_time}')
            self.ui.repeatable_edit_info_widget.setEnabled(False)

            rep_vals_db = ''
            for val in rep_vals:
                rep_vals_db += f'{val} '
            cursor.execute('''UPDATE users SET rep_option=?, rep_vals=? WHERE user=? AND id=?''',
                           (rep_option, rep_vals_db, user, state.cur_task))

            conn.commit()

    def complete_task(self, task_name = None):
        if task_name is None:
            task_name = state.cur_task

        if state.cur_task is None:
            return
        if task_name == state.cur_task:
            state.tasks[state.cur_task]['completed'] = not state.tasks[state.cur_task]['completed']

            cursor.execute('''UPDATE users SET completed=? WHERE user=? AND id=?''',
                           (state.tasks[state.cur_task]['completed'], user, state.cur_task))
            conn.commit()

            self.check_completion()

        else:
            state.tasks[task_name]['completed'] = not state.tasks[task_name]['completed']
            if state.tasks[task_name]['completed']:
                state.tasks[task_name]['taskWidget'].task.task_check.setIcon(QIcon('sources/icons_white/circle-check-big.svg'))
            else:
                state.tasks[task_name]['taskWidget'].task.task_check.setIcon(QIcon('sources/icons_white/circle.svg'))

    def check_completion(self):
        if state.tasks[state.cur_task]['completed']:
            self.ui.task_complete_button.setIcon(QIcon('sources/icons_white/circle-check-big.svg'))
            state.tasks[state.cur_task]['taskWidget'].task.task_check.setIcon(
                QIcon('sources/icons_white/circle-check-big.svg'))
        else:
            self.ui.task_complete_button.setIcon(QIcon('sources/icons_white/circle.svg'))
            state.tasks[state.cur_task]['taskWidget'].task.task_check.setIcon(QIcon('sources/icons_white/circle.svg'))

    def update_progress_bar(self):

        if state.cur_task in state.tasks and len(state.tasks[state.cur_task]['taskSteps']['steps']) != 0:
            progress = (sum(state.tasks[state.cur_task]['taskSteps']['steps'].values()) / len(state.tasks[state.cur_task]['taskSteps']['steps'])) * 100
            state.tasks[state.cur_task]['progress'] = round(progress, 1)
            state.tasks[state.cur_task]['taskWidget'].task.task_progress.setValue(round(progress, 1))

        else:
            progress = 0

        self.ui.task_step_progress.setValue(round(progress, 1))

    def add_task_step(self):
        #mw.steps_stack.setVisible(True)
        self.ui.task_step_progress.setVisible(True)
        print(state.cur_task)
        task_page = state.tasks[state.cur_task]['taskSteps']['page']
        task_page_layout = task_page.layout()
        task_step = TaskStep(parent=task_page)
        task_page_layout.addWidget(task_step.taskstep)

        state.tasks[state.cur_task]['taskSteps']['steps'][task_step.name] = False

        taskstep_data = ''
        for step in state.tasks[state.cur_task]['taskSteps']['steps']:
            completed = state.tasks[state.cur_task]['taskSteps']['steps'][task_step.name]
            taskstep_data += f'{step}{int(completed)}@@'

        cursor.execute('''UPDATE users SET task_steps_infos=? WHERE user=? AND id=?''',
                       (taskstep_data, user, state.cur_task))
        conn.commit()
        self.update_progress_bar()

        self.ui.steps_stack.setMaximumHeight(self.ui.steps_stack.currentWidget().layout().sizeHint().height() + 90)
        self.ui.steps_stack.updateGeometry()

    def setEmptyPage(self, name):
        self.ui.tasks_scrollwidget.layout().removeWidget(state.tasks[state.cur_task]['taskWidget'])

        self.ui.task_info_stack.setCurrentWidget(self.ui.empty_page)
        self.ui.task_info_stack.setVisible(False)

    def change_date(self, mode):
        new_date = state.cur_date + (86400 * mode)
        state.cur_date = new_date

        new_date_str = datetime_str(new_date)
        if new_date_str not in state.dates:

            date_page = QWidget()
            date_page.setObjectName(new_date_str)
            date_page_layout = QVBoxLayout(date_page)

            self.ui.task_list_stack.addWidget(date_page)
            state.dates.append(new_date_str)

        else:
            date_page = self.ui.task_list_stack.findChild(QWidget, new_date_str)

        self.ui.tasks_date_label.setText(new_date_str)
        self.ui.task_list_stack.setCurrentWidget(date_page)

mw = MainWindow()
