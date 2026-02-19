import datetime

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtUiTools import QUiLoader

from config.env_loader import main_ui
from appState import state
from logic.task_steps import TaskStep
from signalHub import signals

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.mw = QUiLoader().load(main_ui, None)

    def setStart(self):
        self.mw.task_step_progress.setVisible(False)
        self.mw.task_info_stack.setVisible(False)

        # self.mw.tabWidget.setCurrentIndex(0)

    def setCustomWidgets(self):
        import ui.widgets.toggle as toggle
        self.mw.repeatable_toggle = toggle.AnimatedToggle(self.mw)
        self.mw.repeatable_widget.layout().replaceWidget(self.mw.rep_switch, self.mw.repeatable_toggle)

    def linkFuncs(self):
        funcs = MWindowFuncs()

        signals.update_progress_bar.connect(funcs.update_progress_bar)
        #popup related
        self.mw.add_task_button.clicked.connect(funcs.show_add_task_popup)

        #taskstep related
        self.mw.add_task_step_button.clicked.connect(funcs.add_task_step)

        #task related
        self.mw.delete_task.clicked.connect(funcs.state.tasks[state.cur_task]['taskWidget'].deconstruct())
        self.mw.every_box.currentTextChanged.connect(funcs.set_mw_every_stack)
        self.mw.repeatable_toggle.toggled.connect(funcs.toggle_mw_repeatable_menu)
        self.mw.task_complete_button.clicked.connect(funcs.complete_task(state.cur_task))
        self.mw.edit_repeatable_button.mode = 'edit'
        self.mw.edit_repeatable_button.clicked.connect(funcs.edit_repeatable)
        self.mw.at_timeedit.timeChanged.connect(funcs.edit_starttime())
        self.mw.due_timeedit.timeChanged.connect(funcs.edit_endtime())

        self.mw.show()

class MWindowFuncs():
    def set_task_info(self, task_name, task_description, task_difficulty, task_category):
        state.cur_task = task_name


        self.mw.task_info_stack.setVisible(True)

        self.mw.task_info_stack.setCurrentIndex(0)
        self.mw.category_stack.setCurrentIndex(0)
        self.mw.difficulty_stack.setCurrentIndex(0)
        self.mw.description_label_edit_layout.setCurrentIndex(0)

        self.mw.task_name_label.setText(task_name)
        self.mw.category.setText(task_category)
        self.mw.difficulty.setText(task_difficulty)  # RENAME THEIR LABELS
        self.mw.description_input_label.setText(task_description)

        self.mw.at_timeedit.setTime(state.tasks[state.cur_task]['duration'][0])
        self.mw.due_timeedit.setTime(state.tasks[state.cur_task]['duration'][1])

        if state.tasks[state.cur_task]['repeatable']['is_repeatable']:
            self.mw.repeatable_set_widget.setVisible(True)
            if not self.mw.repeatable_toggle._checked:
                self.mw.repeatable_toggle.on_click()

            self.mw.task_graphs_widget.setVisible(True)

            next_occurrence_date =  datetime.datetime.fromtimestamp(state.tasks[state.cur_task]['repeatable']['next_occurrence']).strftime("%d.%m.%Y")
            next_occurrence_time =  datetime.datetime.fromtimestamp(state.tasks[state.cur_task]['repeatable']['next_occurrence']).strftime("%H:%M")

            self.mw.next_time_label.setText(f'Next time you will recieve this task on {next_occurrence_date} at {next_occurrence_time}')

            self.mw.every_box.setCurrentIndex(state.tasks[state.cur_task]['repeatable']['rep_option'])
            self.set_mw_every_stack(state.tasks[state.cur_task]['repeatable']['rep_vals'])
        else:
            if self.mw.repeatable_toggle._checked:
                self.mw.repeatable_toggle.on_click()

            self.mw.repeatable_set_widget.setVisible(False)
            self.mw.task_graphs_widget.setVisible(False)

        if len(state.tasks[state.cur_task]['taskSteps']['steps']) == 0:
            self.mw.task_step_progress.setVisible(False)
            self.mw.task_step_progress.setValue(0)
        else:
            self.update_progress_bar()
            self.mw.task_step_progress.setVisible(True)

        if state.tasks[state.cur_task]['completed']:
            self.mw.task_complete_button.setIcon(QIcon('sources/icons_white/circle-check-big.svg'))
        else:
            self.mw.task_complete_button.setIcon(QIcon('sources/icons_white/circle.svg'))

        if state.tasks[task_name]['taskNo'] not in range(self.mw.steps_stack.count()):
            task_step_page = QWidget()
            task_step_page_layout = QVBoxLayout(task_step_page)
            state.tasks[task_name]['taskSteps']['page'] = task_step_page

            self.mw.steps_stack.addWidget(task_step_page)

        self.mw.steps_label.setText(f'{task_name} steps')
        self.mw.steps_stack.setCurrentIndex(state.tasks[task_name]['taskNo'])


        #for i in range(self.mw.steps_stack.currentWidget().layout().count()):
        #    item = self.mw.steps_stack.currentWidget().layout().itemAt(i)
    #
        #    print(item.geometry().width(), item.geometry().height())

        self.mw.steps_stack.setMaximumHeight(self.mw.steps_stack.currentWidget().layout().sizeHint().height())
        self.mw.steps_stack.updateGeometry()

    def edit_starttime(self):

        prev = state.tasks[state.cur_task]['duration'][0]

        state.tasks[state.cur_task]['duration'][0] = self.mw.at_timeedit.time()

        difference = prev.secsTo(self.mw.at_timeedit.time())

        state.tasks[state.cur_task]['repeatable']['next_occurrence'] += difference

        next_occurrence_date = datetime.datetime.fromtimestamp(state.tasks[state.cur_task]['repeatable']['next_occurrence']).strftime("%d.%m.%Y")
        next_occurrence_time = datetime.datetime.fromtimestamp(state.tasks[state.cur_task]['repeatable']['next_occurrence']).strftime("%H:%M")

        self.mw.next_time_label.setText(f'Next time you will recieve this task on {next_occurrence_date} at {next_occurrence_time}')

        state.cur_task_widget = state.tasks[state.cur_task]['taskWidget']
        state.cur_task_widget.start_time = convert_qtTime_str(self.mw.at_timeedit.time())
        state.cur_task_widget.update_duration()

    def edit_endtime(self):

        state.tasks[state.cur_task]['duration'][1] = self.mw.due_timeedit.time()

        state.cur_task_widget = state.tasks[state.cur_task]['taskWidget']
        state.cur_task_widget.end_time = convert_qtTime_str(self.mw.due_timeedit.time())
        state.cur_task_widget.update_duration()

    def toggle_mw_repeatable_menu(self):#On task createon after editing repeatable on prev task
                                    # raises console Error that state.cur_task = ''
                                    # but everything works so idk what is it
        status = self.mw.repeatable_toggle._checked
        self.mw.repeatable_set_widget.setVisible(status)
        state.tasks[state.cur_task]['repeatable']['is_repeatable'] = status

    def set_mw_every_stack(self, vals = None):
        cur_option = self.mw.every_box.currentText()

        self.mw.every_stack.setVisible(True)
        if cur_option == 'Few Days':
            self.mw.every_stack.setCurrentWidget(self.mw.few_days)

            if vals:
                self.mw.few_days_edit.setText(str(vals[0]))
            else:
                self.mw.few_days_edit.setText(popup.few_days_edit.text())

        elif cur_option == 'Week':
            self.mw.every_stack.setCurrentWidget(self.mw.week)
            if vals:
                pass
            else:
                pass
            # to do

        elif cur_option == 'Mounth':
            self.mw.every_stack.setCurrentWidget(self.mw.mounth)

            if vals:
                self.mw.day_edit_2.setText(str(vals[0]))
            else:
                self.mw.day_edit_2.setText(popup.day_edit_2.text())

        elif cur_option == 'Year':
            self.mw.every_stack.setCurrentWidget(self.mw.year)

            if vals:
                self.mw.day_edit.setText(str(vals[0]))
                self.mw.mounth_edit.setCurrentText(vals[1])
            else:
                self.mw.day_edit.setText(popup.day_edit.text())
                self.mw.mounth_edit.setCurrentIndex(popup.mounth_edit.currentIndex())

        elif cur_option == 'Day':
            self.mw.every_stack.setCurrentWidget(self.mw.day)
            self.mw.every_stack.setVisible(False)

    def edit_repeatable(self):
        if self.mw.edit_repeatable_button.mode == 'edit':
            self.mw.edit_repeatable_button.mode = 'apply'
            self.mw.edit_repeatable_button.setIcon(QIcon('sources/icons_white/check.svg'))

            self.mw.repeatable_edit_info_widget.setEnabled(True)
        elif self.mw.edit_repeatable_button.mode == 'apply':
            self.mw.edit_repeatable_button.mode = 'edit'
            self.mw.edit_repeatable_button.setIcon(QIcon('sources/icons_white/pencil.svg'))

            rep_option = self.mw.every_box.currentIndex()
            next_occurrence, rep_vals = (calculate_next_occurrence(
                self.mw.every_box.currentText(),
                self.mw.at_timeedit.time(),
                self.mw
            ))

            state.tasks[state.cur_task]['repeatable']['rep_option'] = rep_option
            state.tasks[state.cur_task]['repeatable']['rep_vals'] = rep_vals
            state.tasks[state.cur_task]['repeatable']['next_occurrence'] = next_occurrence

            next_occurrence_date = datetime.datetime.fromtimestamp(next_occurrence).strftime("%d.%m.%Y")
            next_occurrence_time = datetime.datetime.fromtimestamp(next_occurrence).strftime("%H:%M")

            self.mw.next_time_label.setText(f'Next time you will recieve this task on {next_occurrence_date} at {next_occurrence_time}')
            self.mw.repeatable_edit_info_widget.setEnabled(False)

    def complete_task(self, task_name = state.cur_task):

        if task_name == state.cur_task:
            state.tasks[state.cur_task]['completed'] = not state.tasks[state.cur_task]['completed']
            if state.tasks[state.cur_task]['completed']:
                self.mw.task_complete_button.setIcon(QIcon('sources/icons_white/circle-check-big.svg'))
                state.tasks[state.cur_task]['taskWidget'].task.task_check.setIcon(QIcon('sources/icons_white/circle-check-big.svg'))
            else:
                self.mw.task_complete_button.setIcon(QIcon('sources/icons_white/circle.svg'))
                state.tasks[state.cur_task]['taskWidget'].task.task_check.setIcon(QIcon('sources/icons_white/circle.svg'))

        else:
            state.tasks[task_name]['completed'] = not state.tasks[task_name]['completed']
            if state.tasks[task_name]['completed']:
                state.tasks[task_name]['taskWidget'].task.task_check.setIcon(QIcon('sources/icons_white/circle-check-big.svg'))
            else:
                state.tasks[task_name]['taskWidget'].task.task_check.setIcon(QIcon('sources/icons_white/circle.svg'))

    def update_progress_bar(self):

        if state.cur_task in state.tasks and len(state.taskstasks[state.cur_task]['taskSteps']['steps']) != 0:
            progress = (sum(state.taskstasks[state.cur_task]['taskSteps']['steps'].values()) / len(state.taskstasks[state.cur_task]['taskSteps']['steps'])) * 100
            state.taskstasks[state.cur_task]['progress'] = round(progress, 1)
            state.taskstasks[state.cur_task]['taskWidget'].task.task_progress.setValue(round(progress, 1))

        else:
            progress = 0

        self.mw.task_step_progress.setValue(round(progress, 1))

    def add_task_step(self):
        #mw.steps_stack.setVisible(True)
        self.mw.task_step_progress.setVisible(True)

        task_page = state.taskstasks[state.cur_task]['taskSteps']['page']
        task_page_layout = task_page.layout()
        task_step = TaskStep(parent=task_page)
        task_page_layout.addWidget(task_step.taskstep)

        state.taskstasks[state.cur_task]['taskSteps']['steps'][task_step] = False

        self.update_progress_bar()

        self.mw.steps_stack.setMaximumHeight(self.mw.steps_stack.currentWidget().layout().sizeHint().height() + 90)
        self.mw.steps_stack.updateGeometry()

        #state.taskstasks[state.cur_task]['progress'] = 0