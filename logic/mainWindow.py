import datetime

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtUiTools import QUiLoader

#variables
from config.env_loader import main_ui
from logic.appState import state

#funcs
from logic.core import convert_qtTime_str, calculate_next_occurrence, datetime_str
from logic.signalHub import signals

#instances
from logic.task_steps import TaskStep

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = QUiLoader().load(main_ui, None)

        self.setStart()
        self.setCustomWidgets()
        self.linkFuncs()
        #self.ui.show())

    def setStart(self):
        self.ui.task_step_progress.setVisible(False)
        self.ui.task_info_stack.setVisible(False)

        # self.ui.tabWidget.setCurrentIndex(0)

    def setCustomWidgets(self):
        import ui.widgets.toggle as toggle
        self.ui.repeatable_toggle = toggle.AnimatedToggle(self.ui)
        self.ui.repeatable_widget.layout().replaceWidget(self.ui.rep_switch, self.ui.repeatable_toggle)

    def linkFuncs(self):
        self.funcs = MWindowFuncs(ui = self.ui)

        #signals
        signals.complete_task.connect(lambda name: self.funcs.complete_task(task_name=name))
        signals.update_task_info.connect(lambda *args: self.funcs.set_task_info(*args))
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


class MWindowFuncs():
    def __init__(self, ui):
        self.ui = ui

    def set_task_info(self, task_name, task_description, task_difficulty, task_category):
        ### variables
        state.cur_task = task_name
        task_date = state.tasks[task_name]['taskDate']['date']
        task_no = state.tasks[task_name]['taskNo']
        task_duration = state.tasks[state.cur_task]['duration']
        ### visibility
        self.ui.task_info_stack.setVisible(True)

        self.ui.task_info_stack.setCurrentIndex(0)
        self.ui.category_stack.setCurrentIndex(0)
        self.ui.difficulty_stack.setCurrentIndex(0)
        self.ui.description_label_edit_layout.setCurrentIndex(0)
        ### value assigment
        self.ui.task_name_label.setText(task_name)
        self.ui.category.setText(task_category)
        self.ui.difficulty.setText(task_difficulty)  # RENAME THEIR LABELS
        self.ui.description_input_label.setText(task_description)
        self.ui.at_timeedit.setTime(task_duration[0])
        self.ui.due_timeedit.setTime(task_duration[1])
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
            task_step_page = QWidget()
            task_step_page_layout = QVBoxLayout(task_step_page)
            state.tasks[task_name]['taskSteps']['page'] = task_step_page

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

        state.tasks[task_name]['taskDate']['page'] = date_page
        date_page.layout().addWidget(state.tasks[task_name]['taskWidget'].task)
        self.ui.task_list_stack.setCurrentWidget(date_page)
#       ###
    def edit_starttime(self):
        if state.cur_task is None:
            return
        prev = state.tasks[state.cur_task]['duration'][0]
        cur_task_widget = state.tasks[state.cur_task]['taskWidget']

        state.tasks[state.cur_task]['duration'][0] = self.ui.at_timeedit.time()

        cur_task_widget.start_time = convert_qtTime_str(self.ui.at_timeedit.time())

        if self.ui.at_timeedit.time() > state.tasks[state.cur_task]['duration'][1]:
            state.tasks[state.cur_task]['duration'][1] = self.ui.at_timeedit.time()
            cur_task_widget.end_time = convert_qtTime_str(self.ui.at_timeedit.time())

            self.ui.due_timeedit.setTime(self.ui.at_timeedit.time())
        cur_task_widget.update_duration()

        if state.tasks[state.cur_task]['repeatable']['next_occurrence'] is not None:
            difference = prev.secsTo(self.ui.at_timeedit.time())

            state.tasks[state.cur_task]['repeatable']['next_occurrence'] += difference

            next_occurrence_date = datetime.datetime.fromtimestamp(state.tasks[state.cur_task]['repeatable']['next_occurrence']).strftime("%d.%m.%Y")
            next_occurrence_time = datetime.datetime.fromtimestamp(state.tasks[state.cur_task]['repeatable']['next_occurrence']).strftime("%H:%M")

            self.ui.next_time_label.setText(f'Next time you will recieve this task on {next_occurrence_date} at {next_occurrence_time}')

    def edit_endtime(self):

        state.tasks[state.cur_task]['duration'][1] = self.ui.due_timeedit.time()

        cur_task_widget = state.tasks[state.cur_task]['taskWidget']
        cur_task_widget.end_time = convert_qtTime_str(self.ui.due_timeedit.time())

        if self.ui.due_timeedit.time() < state.tasks[state.cur_task]['duration'][0]:
            state.tasks[state.cur_task]['duration'][0] = self.ui.due_timeedit.time()
            cur_task_widget.start_time = convert_qtTime_str(self.ui.due_timeedit.time())

            self.ui.at_timeedit.setTime(self.ui.due_timeedit.time())

        cur_task_widget.update_duration()

    def toggle_mw_repeatable_menu(self):
        status = self.ui.repeatable_toggle._checked
        self.ui.repeatable_set_widget.setVisible(status)
        state.tasks[state.cur_task]['repeatable']['is_repeatable'] = status

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

    def complete_task(self, task_name = None):
        if task_name is None:
            task_name = state.cur_task

        if state.cur_task is None:
            return
        if task_name == state.cur_task:
            state.tasks[state.cur_task]['completed'] = not state.tasks[state.cur_task]['completed']
            if state.tasks[state.cur_task]['completed']:
                self.ui.task_complete_button.setIcon(QIcon('sources/icons_white/circle-check-big.svg'))
                state.tasks[state.cur_task]['taskWidget'].task.task_check.setIcon(QIcon('sources/icons_white/circle-check-big.svg'))
            else:
                self.ui.task_complete_button.setIcon(QIcon('sources/icons_white/circle.svg'))
                state.tasks[state.cur_task]['taskWidget'].task.task_check.setIcon(QIcon('sources/icons_white/circle.svg'))

        else:
            state.tasks[task_name]['completed'] = not state.tasks[task_name]['completed']
            if state.tasks[task_name]['completed']:
                state.tasks[task_name]['taskWidget'].task.task_check.setIcon(QIcon('sources/icons_white/circle-check-big.svg'))
            else:
                state.tasks[task_name]['taskWidget'].task.task_check.setIcon(QIcon('sources/icons_white/circle.svg'))

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

        task_page = state.tasks[state.cur_task]['taskSteps']['page']
        task_page_layout = task_page.layout()
        task_step = TaskStep(parent=task_page)
        task_page_layout.addWidget(task_step.taskstep)

        state.tasks[state.cur_task]['taskSteps']['steps'][task_step] = False

        self.update_progress_bar()

        self.ui.steps_stack.setMaximumHeight(self.ui.steps_stack.currentWidget().layout().sizeHint().height() + 90)
        self.ui.steps_stack.updateGeometry()

    def setEmptyPage(self, name):
        self.ui.tasks_scrollwidget.layout().removeWidget(state.tasks[name]['taskWidget'])

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
