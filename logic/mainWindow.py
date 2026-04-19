import csv
import datetime
import json
import webbrowser
from traceback import print_tb

from PySide6.QtCharts import QLineSeries, QChart, QChartView, QDateTimeAxis, QValueAxis
from PySide6.QtCore import QDateTime, Qt
from PySide6.QtGui import QIcon, QPixmap, QBrush, QColor
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QFileDialog, QSizePolicy
from PySide6.QtUiTools import QUiLoader

#variables
from config.env_loader import main_ui, user, data
from data.data_to_plot import MyPlot
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

        self.setCustomWidgets()
        self.setUI()
        self.funcs.loadTasks()
        self.linkFuncs()
        #self.ui.show())

    def setUI(self):
        self.ui.task_step_progress.setVisible(False)
        self.ui.task_info_stack.setVisible(False)

        self.ui.tabWidget.setCurrentIndex(0)

        self.ui.theme_box.setCurrentText(data['cur_theme']) #!

        self.funcs.setTheme()
        self.funcs.setLang()
        self.funcs.setPanelPos()

    def setCustomWidgets(self):
        from logic.widgets import  AnimatedToggle
        self.ui.repeatable_toggle = AnimatedToggle(self.ui)
        self.ui.repeatable_widget.layout().replaceWidget(self.ui.rep_switch, self.ui.repeatable_toggle)

        ##1st, line plot
        created_completed_line = MyPlot()
        created_completed_line.tasks_created_plot(accumulation=0)
        chart = created_completed_line.chart

        self.ui.tasks_created_cv = QChartView(chart)
        self.ui.tasks_created_cv.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.tasks_created_cv.setMinimumSize(0, 450);

        parent_layout = self.ui.task_line.parentWidget().layout()
        parent_layout.replaceWidget(self.ui.task_line, self.ui.tasks_created_cv)
        ##second, pie plot
        completed_ratio_pie = MyPlot()
        completed_ratio_pie.completed_ratio()
        chart = completed_ratio_pie.chart

        self.ui.completed_ratio_cv = QChartView(chart)
        self.ui.completed_ratio_cv.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.completed_ratio_cv.setMinimumSize(0, 450);

        parent_layout = self.ui.perc_task_pie.parentWidget().layout()
        parent_layout.replaceWidget(self.ui.perc_task_pie, self.ui.completed_ratio_cv)

        #4, pie plot

        diff_ratio_pie = MyPlot()
        diff_ratio_pie.diff_ratio()
        chart = diff_ratio_pie.chart

        self.ui.diff_ratio_cv = QChartView(chart)
        self.ui.diff_ratio_cv.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.diff_ratio_cv.setMinimumSize(0, 350);

        parent_layout = self.ui.diff_pie.parentWidget().layout()
        parent_layout.replaceWidget(self.ui.diff_pie, self.ui.diff_ratio_cv)

        #6, pie plot

        categ_ratio_pie = MyPlot()
        categ_ratio_pie.categ_ratio()
        chart = categ_ratio_pie.chart

        self.ui.categ_ratio_cv = QChartView(chart)
        self.ui.categ_ratio_cv.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.categ_ratio_cv.setMinimumSize(0, 350);

        parent_layout = self.ui.categ_pie.parentWidget().layout()
        print('ge 0', parent_layout)
        parent_layout.replaceWidget(self.ui.categ_pie, self.ui.categ_ratio_cv)


        #7, bar plot
        diff_day_bar = MyPlot()
        diff_day_bar.day_diff_ratio()
        chart = diff_day_bar.chart
#
        self.ui.diff_day_cv = QChartView(chart)
        self.ui.diff_day_cv.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.diff_day_cv.setMinimumSize(0, 450);
#
        parent_layout = self.ui.diff_bar.parentWidget().layout()
        print('ge ',parent_layout)
        parent_layout.replaceWidget(self.ui.diff_bar, self.ui.diff_day_cv)
        #maybe make it using cycle ^
    def linkFuncs(self):
        #signals
        signals.complete_task.connect(lambda name: self.funcs.complete_task(taskId=name))
        signals.update_task_info.connect(lambda taksId: self.funcs.set_task_info(taksId))
        signals.update_progress_bar.connect(lambda: self.funcs.update_progress_bar())
        signals.setEmptyPage.connect(lambda name: self.funcs.setEmptyPage(name=name))
        #popup related
        self.ui.add_task_button.clicked.connect(lambda : signals.show_add_task_popup.emit())

        #taskstep related
        self.ui.add_task_step_button.clicked.connect(lambda : self.funcs.add_task_step())

        #task related
        self.ui.delete_task.clicked.connect(lambda : state.tasks[state.cur_task]['taskWidget'].deconstruct())
        #!
        self.ui.every_box.currentTextChanged.connect(lambda : self.funcs.set_mw_every_stack(state.tasks[state.cur_task]['repeatable']['rep_vals']) )
        self.ui.repeatable_toggle.toggled.connect(lambda : self.funcs.toggle_mw_repeatable_menu())
        self.ui.task_complete_button.clicked.connect(lambda : self.funcs.complete_task(state.cur_task))
        self.ui.edit_repeatable_button.mode = 'edit'
        self.ui.edit_repeatable_button.clicked.connect(lambda : self.funcs.edit_repeatable())
        self.ui.at_timeedit.timeChanged.connect(lambda : self.funcs.edit_starttime())
        self.ui.due_timeedit.timeChanged.connect(lambda : self.funcs.edit_endtime())
        self.ui.tasks_prev_button.clicked.connect(lambda : self.funcs.change_date(-1))
        self.ui.tasks_next_button.clicked.connect(lambda : self.funcs.change_date(1))

        #settings related
        self.ui.theme_box.currentTextChanged.connect(lambda : self.funcs.changeTheme())
        self.ui.lang_box.currentTextChanged.connect(lambda : self.funcs.changeLang())
        self.ui.panel_loc_box.currentTextChanged.connect(lambda : self.funcs.changePanelPos())

        self.ui.export_data_button.clicked.connect(lambda : self.funcs.exportData())
        #webbrowser.open("https://github.com/YotaBitOn")
        self.ui.git_button.clicked.connect(lambda : webbrowser.open("https://github.com/YotaBitOn"))


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
            #!
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
        cur_option = self.ui.every_box.currentData()

        self.ui.every_stack.setVisible(True)
        if cur_option == 'few_days':
            self.ui.every_stack.setCurrentWidget(self.ui.few_days)
            if vals:
                self.ui.few_days_edit.setText(str(vals[0]))

        elif cur_option == 'week':
            self.ui.every_stack.setCurrentWidget(self.ui.week)
            # to do

        elif cur_option == 'month':
            self.ui.every_stack.setCurrentWidget(self.ui.mounth)

            if vals:
                self.ui.day_edit_2.setText(str(vals[0]))

        elif cur_option == 'year':
            self.ui.every_stack.setCurrentWidget(self.ui.year)

            if vals:
                self.ui.day_edit.setText(str(vals[0]))
                if len(vals) > 1:
                    self.ui.mounth_edit.setCurrentText(vals[1])

        elif cur_option == 'day':
            self.ui.every_stack.setCurrentWidget(self.ui.day)
            self.ui.every_stack.setVisible(False)

    def edit_repeatable(self):
        if self.ui.edit_repeatable_button.mode == 'edit':


            self.ui.edit_repeatable_button.mode = 'apply'
            self.ui.edit_repeatable_button.setIcon(QIcon('sources/icons_white/check.svg'))

            self.ui.repeatable_edit_info_widget.setEnabled(True)

            for child in self.ui.repeatable_edit_info_widget.findChildren(QWidget):
                child.setEnabled(True)




        elif self.ui.edit_repeatable_button.mode == 'apply':
            self.ui.edit_repeatable_button.mode = 'edit'
            self.ui.edit_repeatable_button.setIcon(QIcon('sources/icons_white/pencil.svg'))

            rep_option = self.ui.every_box.currentIndex()

            next_occurrence, rep_vals = (calculate_next_occurrence(self))
            state.tasks[state.cur_task]['repeatable']['rep_option'] = rep_option
            state.tasks[state.cur_task]['repeatable']['rep_vals'] = rep_vals
            state.tasks[state.cur_task]['repeatable']['next_occurrence'] = next_occurrence

            next_occurrence_date = datetime.datetime.fromtimestamp(next_occurrence).strftime("%d.%m.%Y")
            next_occurrence_time = datetime.datetime.fromtimestamp(next_occurrence).strftime("%H:%M")

            self.ui.next_time_label.setText(f'Next time you will recieve this task on {next_occurrence_date} at {next_occurrence_time}')
            self.ui.repeatable_edit_info_widget.setEnabled(False)
            for child in self.ui.repeatable_edit_info_widget.findChildren(QWidget):
                child.setEnabled(False)

            rep_vals_db = ''
            for val in rep_vals:
                rep_vals_db += f'{val} '
            cursor.execute('''UPDATE users SET rep_option=?, rep_vals=? WHERE user=? AND id=?''',
                           (rep_option, rep_vals_db, user, state.cur_task))

            conn.commit()

    def complete_task(self, taskId = None):
        if taskId == None:
            taskId = state.cur_task

        if state.cur_task is None:
            return

        state.tasks[taskId]['completed'] = not state.tasks[taskId]['completed']

        completed_at = 0
        if state.tasks[taskId]['completed']:
            completed_at = datetime.datetime.now().timestamp()

        cursor.execute('''UPDATE users SET completed=?, completed_at=? WHERE user=? AND id=?''',
                       (state.tasks[taskId]['completed'], completed_at , user, taskId))
        conn.commit()

        if taskId == state.cur_task:
            self.check_completion()

        else:
            if state.tasks[taskId]['completed']:
                state.tasks[taskId]['taskWidget'].task.task_check.setIcon(QIcon('sources/icons_white/circle-check-big.svg'))
            else:
                state.tasks[taskId]['taskWidget'].task.task_check.setIcon(QIcon('sources/icons_white/circle.svg'))

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

            #date_page = QWidget()
            #date_page.setObjectName(new_date_str)
            #date_page_layout = QVBoxLayout(date_page)
            #self.ui.task_list_stack.addWidget(date_page)

            self.loadTasks()
            state.dates.append(new_date_str)

        else:
            date_page = self.ui.task_list_stack.findChild(QWidget, new_date_str)
            self.ui.task_list_stack.setCurrentWidget(date_page)
        self.ui.tasks_date_label.setText(new_date_str)


    def changeTheme(self):
        data['cur_theme'] = self.ui.theme_box.currentData()

        with open("config/config.json", "w") as f:
            json.dump(data, f, indent=4)

        self.setTheme()

        signals.change_theme.emit()

    def setTheme(self):

        main_color = data['palette'][data['theme'][data['cur_theme']]['main']]
        section_color = data['palette'][data['theme'][data['cur_theme']]['section']]
        button_color = data['palette'][data['theme'][data['cur_theme']]['button']]
        field_color = data['palette'][data['theme'][data['cur_theme']]['field']]
        text_color = data['palette'][data['theme'][data['cur_theme']]['text']]

        #icons
        self.setIcons()

        #main
        self.ui.setStyleSheet(f'''background-color:rgb({main_color});
                                color:rgb({text_color});''')


        #sections
        self.ui.main_info_widget.setStyleSheet(f'''background-color:rgb({section_color});
                                color:rgb({text_color});
                                border-radius: 40px;''')

        self.ui.task_steps_widget.setStyleSheet(f'''background-color:rgb({section_color});
                                        color:rgb({text_color});
                                        border-radius: 40px;''')

        self.ui.repeatable_widget.setStyleSheet(f'''background-color:rgb({section_color});
                                        color:rgb({text_color});
                                        border-radius: 40px;''')

        self.ui.task_graphs_widget.setStyleSheet(f'''background-color:rgb({section_color});
                                        color:rgb({text_color});
                                        border-radius: 40px;''')

        self.ui.tasks_date.setStyleSheet(f'''background-color:rgb({section_color});
                                        color:rgb({text_color});
                                        border: none;
                                        border-radius: 15px;''')
        #buttons
        self.ui.add_task_button.setStyleSheet(f'''background-color:rgb({button_color});
                                                color:rgb({text_color});
                                                border: none;
                                                border-radius: 15px;''')

        self.ui.add_task_step_button.setStyleSheet(f'''background-color:rgb({button_color});
                                                        color:rgb({text_color});
                                                        border: none;
                                                        border-radius: 15px;''')

        self.ui.edit_repeatable_button.setStyleSheet(f'''background-color:rgb({button_color});
                                                        color:rgb({text_color});
                                                        border: none;
                                                        border-radius: 15px;''')

        self.ui.delete_task.setStyleSheet(f'''background-color:rgb({button_color});
                                                        color:rgb({text_color});
                                                        border: none;
                                                        border-radius: 15px;''')
        #fields
        self.ui.at_timeedit.setStyleSheet(f'''background-color:rgb({field_color});
                                        color:rgb({text_color});
                                        border: none;
                                        border-radius: 10px;''')

        self.ui.due_timeedit.setStyleSheet(f'''background-color:rgb({field_color});
                                                color:rgb({text_color});
                                                border: none;
                                                border-radius: 10px;''')

        self.ui.every_box.setStyleSheet(f'''background-color:rgb({field_color});
                                        color:rgb({text_color});''')

        self.ui.day_edit_2.setStyleSheet(f'''background-color:rgb({field_color});
                                                color:rgb({text_color});''')

        self.ui.day_edit.setStyleSheet(f'''background-color:rgb({field_color});
                                        color:rgb({text_color});''')

        self.ui.mounth_edit.setStyleSheet(f'''background-color:rgb({field_color});
                                                color:rgb({text_color});''')

        self.ui.few_days_edit.setStyleSheet(f'''background-color:rgb({field_color});
                                        color:rgb({text_color});''')

        self.ui.description_text_edit.setStyleSheet(f'''background-color:rgb({field_color});
                                                color:rgb({text_color});''')

        self.ui.difficulty_combobox.setStyleSheet(f'''background-color:rgb({field_color});
                                              color:rgb({text_color});''')

        self.ui.category_combobox.setStyleSheet(f'''background-color:rgb({field_color});
                                                color:rgb({text_color});''')

        self.ui.description_input_label.setStyleSheet(f'''background-color:rgb({field_color});
                                                color:rgb({text_color});''')

        self.ui.graph_scrollwidget.setStyleSheet(f"""
            #categ_bar_widget, #categ_pie_widget, #diff_bar_widget, #diff_pie_widget, #perc_task_widget, #task_widget {{
                background-color: rgb({section_color});
                border: 2px solid black;
                border-radius: 15px;
            }}

            #categ_bar_widget, #categ_pie_widget, #diff_bar_widget, #diff_pie_widget, #perc_task_widget, #task_widget * {{
                background: transparent;
            }}
        """)

        self.ui.every_stack.setStyleSheet(f"""
        QWidget{{
        background-color: rgb({field_color});
        border: none;
        border-radius: 10px;
        }}
        
        QPushButton{{
        background-color: rgba(255, 255, 255, 0);
        border: 2px solid white;
        border-radius: 25px;
        }}""")

        try:
            main_color = data['palette'][data['theme'][data['cur_theme']]['section']]
            r, g, b = map(int, main_color.split(','))
            self.ui.tasks_created_cv.chart().setBackgroundBrush(QBrush(QColor(r, g, b)))
            self.ui.completed_ratio_cv.chart().setBackgroundBrush(QBrush(QColor(r, g, b)))
            self.ui.diff_ratio_cv.chart().setBackgroundBrush(QBrush(QColor(r, g, b)))
            self.ui.categ_ratio_cv.chart().setBackgroundBrush(QBrush(QColor(r, g, b)))
            self.ui.diff_day_cv.chart().setBackgroundBrush(QBrush(QColor(r, g, b)))

        except:
            print('No chart found')
    def changeLang(self):
        data['cur_lang'] = self.ui.lang_box.currentData()

        with open("config/config.json", "w") as f:
            json.dump(data, f, indent=4)

        self.setLang()
        signals.change_lang.emit()

    def setLang(self):

        cur_lang = data['cur_lang']

        with open(f"config/langs/{cur_lang}.json", "r") as f:
            lang = json.load(f)

        translations_map = {
            # Tasks
            self.ui.difficulty_label: "difficulty.label",
            self.ui.category_label: "category.label",
            self.ui.description_label: "task.description",
            self.ui.duration_label: "task.duration",
            self.ui.steps_label: "task.steps",
            self.ui.repeatable_label: "repeatable.label",
            self.ui.next_time_label: "repeatable.next_occurrence",
            self.ui.every_label: "repeat.every",
            self.ui.on_day_label: "repeat.on_day",
            self.ui.on_label: "repeat.on",
            self.ui.few_days_label: "repeat.how_many_days",

            # Analytics
            self.ui.analytics_label: "analytics.label",
            self.ui.task_widget_label: "analytics.tasks_created",
            self.ui.perc_task_label: "analytics.tasks_completion_percent",
            self.ui.diff_bar_label: "analytics.tasks_by_difficulty",
            self.ui.diff_pie_label: "analytics.difficulty_distribution",
            self.ui.categ_bar_label: "analytics.tasks_by_category",
            self.ui.categ_pie_label: "analytics.category_distribution",

            # Settings
            self.ui.theme_label: "settings.theme",
            self.ui.lang_label: "settings.lang",
            self.ui.panel_loc_label: "settings.panel_location",
            self.ui.difficulty_enable_label: "settings.show_difficulty",
            self.ui.category_enable_label: "settings.show_category",
            self.ui.export_data_button: "settings.export_data",
            self.ui.contact_dev_label: "settings.contact_dev",
            self.ui.login_button: "settings.login",

            # User
            self.ui.cur_goals_label: "user.current_goals",
            self.ui.choose_tp_label: "user.completed_goals",
            self.ui.activity_label: "user.tasks_completed",
        }

        # Apply all translations
        for widget, key in translations_map.items():
            widget.setText(lang[key])

        #nav
        self.ui.tabWidget.setTabText(0, lang["nav.tasks"])
        self.ui.tabWidget.setTabText(1, lang["nav.analytics"])
        self.ui.tabWidget.setTabText(2, lang["nav.settings"])
        self.ui.tabWidget.setTabText(3, lang["nav.user"])
        self.ui.tabWidget.setTabText(4, lang["nav.clock"])

        #combos
        combos_map = {

            self.ui.category_combobox: {  #  actually holds difficulty items (names swapped in .ui)
                'Free': 'free',
                lang['difficulty.easy']: 'easy',
                lang['difficulty.medium']: 'medium',
                lang['difficulty.hard']: 'hard',
            },

            self.ui.difficulty_combobox: {  #  actually holds category items (names swapped in .ui)
                lang['category.sport']: 'sport',
                lang['category.finance']: 'finance',
                lang['category.education']: 'education',
                lang['category.health']: 'health',
                lang['category.social']: 'social',
                lang['category.meal']: 'meal',
                lang['category.chores']: 'chores',
                lang['category.job']: 'job',
                lang['category.hygiene']: 'hygiene',
                lang['category.mental']: 'mental',
                lang['category.rest']: 'rest',
                lang['category.other']: 'other',
            },

            self.ui.every_box: {
                lang['repeat.day']: 'day',
                lang['repeat.few_days']: 'few_days',
                lang['repeat.week']: 'week',
                lang['repeat.month']: 'month',
                lang['repeat.year']: 'year',
            },

            self.ui.mounth_edit: {
                lang['month.january']: 1,
                lang['month.february']: 2,
                lang['month.march']: 3,
                lang['month.april']: 4,
                lang['month.may']: 5,
                lang['month.june']: 6,
                lang['month.july']: 7,
                lang['month.august']: 8,
                lang['month.september']: 9,
                lang['month.october']: 10,
                lang['month.november']: 11,
                lang['month.december']: 12,
            },

            self.ui.choose_way: {
                lang['repeat.day']: 'day',
                lang['repeat.week']: 'week',
                lang['repeat.month']: 'month',
                lang['repeat.year']: 'year',
                'All time': 'all',  # no lang key exists for this
            },

            self.ui.analytics_year_1: {
                '2026': 2026,
                '2027': 2027,
            },

            self.ui.analytics_mounth: {
                lang['month.january']: 1,
                lang['month.february']: 2,
                lang['month.march']: 3,
                lang['month.april']: 4,
                lang['month.may']: 5,
                lang['month.june']: 6,
                lang['month.july']: 7,
                lang['month.august']: 8,
                lang['month.september']: 9,
                lang['month.october']: 10,
                lang['month.november']: 11,
                lang['month.december']: 12,
            },

            self.ui.analytics_year_2: {
                '2026': 2026,
                '2027': 2027,
            },

            self.ui.lang_box: {
                'English': 'eng',
                'Українська': 'ua',
                'Slovenčina': 'sk',
            },

            self.ui.panel_loc_box: {
                'Left': 'West',
                'Right': 'East',
                'Top': 'North',
                'Bottom': 'South',
            },

            self.ui.theme_box: {
                lang['settings.theme.dark']: 'dark',
                lang['settings.theme.light']: 'light',
            },

            self.ui.choose_dmya_box: {
                lang['repeat.day']: 'day',
                lang['repeat.week']: 'week',
                lang['repeat.month']: 'month',
                lang['repeat.year']: 'year',
                'All time': 'all',
            },

            self.ui.user_year_2: {
                '2026': 2026,
                '2027': 2027,
            },

            self.ui.user_mounth: {
                lang['month.january']: 1,
                lang['month.february']: 2,
                lang['month.march']: 3,
                lang['month.april']: 4,
                lang['month.may']: 5,
                lang['month.june']: 6,
                lang['month.july']: 7,
                lang['month.august']: 8,
                lang['month.september']: 9,
                lang['month.october']: 10,
                lang['month.november']: 11,
                lang['month.december']: 12,
            },

            self.ui.user_year_1: {
                '2026': 2026,
                '2027': 2027,
            },

        }


        for comboBox in combos_map:
            comboBox.blockSignals(True)

            comboBox.clear()
            for item in combos_map[comboBox]:
                comboBox.addItem(item, combos_map[comboBox][item])

            comboBox.blockSignals(False)

        self.ui.lang_box.blockSignals(True)
        self.ui.lang_box.setCurrentIndex(self.ui.lang_box.findData(cur_lang))
        self.ui.lang_box.blockSignals(False)

        self.ui.theme_box.blockSignals(True)
        self.ui.theme_box.setCurrentIndex(self.ui.theme_box.findData(data['cur_theme']))
        self.ui.theme_box.blockSignals(False)

        self.ui.panel_loc_box.blockSignals(True)
        self.ui.panel_loc_box.setCurrentIndex(self.ui.panel_loc_box.findData(data['panel_pos']))
        self.ui.panel_loc_box.blockSignals(False)

    def changePanelPos(self):
        data['panel_pos'] = self.ui.panel_loc_box.currentData()

        with open("config/config.json", "w") as f:
            json.dump(data, f, indent=4)

        self.setPanelPos()

    def setPanelPos(self):
        if data['panel_pos'] == 'West':
            self.ui.tabWidget.setTabPosition(QTabWidget.West)

        if data['panel_pos'] == 'East':
            self.ui.tabWidget.setTabPosition(QTabWidget.East)

        if data['panel_pos'] == 'North':
            self.ui.tabWidget.setTabPosition(QTabWidget.North)

        if data['panel_pos'] == 'South':
            self.ui.tabWidget.setTabPosition(QTabWidget.South)

    def setIcons(self):
        cur_icons = data['theme'][data['cur_theme']]['icons']

        icons_map = {
            self.ui.tasks_prev_button: 'chevron-left',
            self.ui.tasks_next_button: 'chevron-right',
            self.ui.add_task_button: 'plus',
            self.ui.task_complete_button: 'circle',
            self.ui.add_task_step_button: 'plus',
            self.ui.edit_repeatable_button: 'pencil',
            self.ui.cur_streak_icon: 'flame',
            self.ui.best_streak_icon: 'flame',
            self.ui.delete_task: 'trash',
            #self.ui.telegram_button: 'telegram',
            self.ui.git_button: 'github'
        }

        for widget, icon_name in icons_map.items():
            widget.setIcon(QIcon(f'sources/icons_{cur_icons}/{icon_name}.svg'))

        # QLabel uses setPixmap instead of setIcon
        self.ui.acc_icon.setPixmap(QPixmap(f'sources/icons_{cur_icons}/user-round.svg'))

    def exportData(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self.ui,
            "Зберегти CSV",
            "",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            writer.writerow(column_names)
            writer.writerows(rows)

    def loadTasks(self):
        ### task widget setting
        print('Loading tasks for ', datetime_str(state.cur_date))

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
                    id,
                    created_at,
                    completed_at              
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
                try:
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
                    created_at = task[13]
                    completed_at = task[14]
                    state.cur_task = taskId


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


                        for step in taskSteps.split('@@')[:-1]:

                            step_name, step_completed = step[:-1], int(step[-1])
                            state.tasks[taskId]['taskSteps']['steps'][step_name] = step_completed

                            # mw.steps_stack.setVisible(True)

                            #task_page = state.tasks[state.cur_task]['taskSteps']['page']
                            task_page_layout = task_step_page.layout()
                            task_step = TaskStep(step_name, parent=task_step_page)
                            task_page_layout.addWidget(task_step.taskstep)

                            state.tasks[state.cur_task]['taskSteps']['steps'][step_name] = step_completed

                            self.update_progress_bar()

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

                        self.ui.next_time_label.setText(f'Next time you will recieve this task on {next_occurrence_date} at {next_occurrence_time}')
                        #!
                        self.ui.every_box.setCurrentIndex(state.tasks[state.cur_task]['repeatable']['rep_option'])
                        self.set_mw_every_stack(state.tasks[state.cur_task]['repeatable']['rep_vals'])


                    state.tasks[taskId]['taskDate']['page'] = date_page
                    date_page.layout().addWidget(state.tasks[taskId]['taskWidget'].task)

                    state.task_ammo += 1

                    self.check_completion()
                    state.print_tasks()
                except Exception as e:
                    print(f'Problem for task #{task[12]} occured: \n', e)
                    delete_task = input(f'Task #{task[12]} is corrupted, delete it?(y/n)')
                    if delete_task.lower() == 'y':
                        cursor.execute('''DELETE FROM users WHERE id=?''', (task[12],))

                        conn.commit()

                        print(f'Task #{task[12]} was deleted')
                    else:
                        print(f'Task #{task[12]} was skipped')


mw = MainWindow()

