import datetime
import json

from PySide6.QtUiTools import QUiLoader

#variables
from config.env_loader import popup_ui, user, data
from logic.appState import state

#funcs
from logic.core import convert_qtTime_int, calculate_next_occurrence, datetime_str
from logic.signalHub import signals

#instances
from data.init_db import conn, cursor
from logic.mainWindow import mw
from logic.widgets import Task, AnimatedToggle


class Popup():
    def __init__(self):
        self.ui = QUiLoader().load(popup_ui, None)

        signals.change_lang.connect(lambda : self.setLang())

        self.setUI()
    def setUI(self):

        self.ui.repeatable_toggle = AnimatedToggle(self.ui)
        self.ui.repeatable_layout.replaceWidget(self.ui.rep_switch, self.ui.repeatable_toggle)
        self.ui.repeatable_toggle.toggled.connect(self.set_popup_repeatable_menu)

        self.ui.submit_button.clicked.connect(self.submit)

        self.ui.every_box.currentTextChanged.connect(self.set_popup_every_stack)

        self.setLang()
        #signals.show_add_task_self.ui.connect(lambda :self.show_add_task_popup())
        #self.show_add_task_popup()

    def show_add_task_popup(self):

        self.ui.repeatable_widget.setVisible(False)
        self.ui.every_stack.setCurrentWidget(self.ui.day)
        self.ui.every_stack.setVisible(False)

        self.ui.show()

    def set_popup_repeatable_menu(self):
        self.ui.repeatable_widget.setVisible(self.ui.repeatable_toggle._checked)

    def set_popup_every_stack(self):
        cur_option = self.ui.every_box.currentText()

        self.ui.every_stack.setVisible(True)
        if cur_option == 'few_days':
            self.ui.every_stack.setCurrentWidget(self.ui.few_days)

        elif cur_option == 'week':
            self.ui.every_stack.setCurrentWidget(self.ui.week)

        elif cur_option == 'month':
            self.ui.every_stack.setCurrentWidget(self.ui.mounth)

        elif cur_option == 'year':
            self.ui.every_stack.setCurrentWidget(self.ui.year)

        elif cur_option == 'day':
            self.ui.every_stack.setCurrentWidget(mw.day)
            self.ui.every_stack.setVisible(False)

    def submit(self):
        ### variables
        _task_name = self.ui.name_edit.text()
        taskId = int(datetime.datetime.now().timestamp())

        state.cur_task = taskId
        _task_repeatable = self.ui.repeatable_toggle._checked

        if _task_name == '':
            _task_name = f"Task #{state.task_ammo}"

        _task_description = self.ui.description_edit.toPlainText()
        _task_difficulty = self.ui.diff_box.currentData()
        _task_category = self.ui.difficulty_combobox.currentData()  # rename it pls

        start_time = convert_qtTime_int(self.ui.at_timeedit.time())
        end_time = convert_qtTime_int(self.ui.due_timeedit.time())

        task_date = datetime_str(state.cur_date)
        ### repeatable setting
        next_occurrence = rep_option = rep_vals = None
        if _task_repeatable:
            mw.ui.repeatable_set_widget.setVisible(True)

            rep_option = self.ui.every_box.currentIndex()
            next_occurrence, rep_vals = (calculate_next_occurrence(self))
            mw.ui.every_box.setCurrentIndex(self.ui.every_box.currentIndex())
            mw.funcs.set_mw_every_stack(rep_vals)
        else:
            if mw.ui.repeatable_toggle._checked:
                mw.ui.repeatable_toggle.on_click()
            mw.ui.repeatable_set_widget.setVisible(False)

        ### prepare data to sending

        str_rep_vals = ''
        if _task_repeatable:
            for val in rep_vals:
                str_rep_vals += str(val)
                str_rep_vals += ' '
        ### send data to db
        cursor.execute("""
        INSERT INTO users
        (
        id,
        user,
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
        description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (taskId, user, _task_name, task_date, start_time, end_time, _task_difficulty, _task_category, 0,
        _task_repeatable, rep_option, str_rep_vals, '', _task_description))
        conn.commit()  #<-----------IMPORTANT (off for test cases)

        ### task widget setting
        task = Task(taskId, _task_name, _task_description, _task_difficulty, _task_category, start_time, end_time,
                    parent=None)  #change it
        ### tasks dict setting !!!! THIS DICT IS PLANNED TO BE REPLACED WiTH DB!!! one day, mark my words
        state.tasks[taskId] = {
            'taskName': _task_name,
            'taskNo': state.task_ammo,
            'taskWidget': task,
            'difficulty': _task_difficulty,
            'category': _task_category,
            'description': _task_description,
            'completed': False,
            'duration': [convert_qtTime_int(self.ui.at_timeedit.time()),
                         convert_qtTime_int(self.ui.due_timeedit.time())],
            'taskDate': {
                'date': task_date,
                'page': None
            },
            'taskSteps': {
                'steps': {},
                'page': None
            },
            'repeatable': {
                'is_repeatable': _task_repeatable,
                'next_occurrence': next_occurrence,
                'rep_option': rep_option,
                'rep_vals': rep_vals
            }
        }
        state.task_ammo += 1
        ### passing setting further process to main window and closing
        mw.funcs.set_task_info(taskId)
        self.ui.close()

    def setLang(self):
        with open(f"config/config.json", "r") as f:
            data = json.load(f)
        cur_lang = data['cur_lang']
        print('67 ',data)
        with open(f"config/langs/{cur_lang}.json", "r") as f:
            lang = json.load(f)

        translations_map = {
            # Basic info
            self.ui.name_label: "task.name",
            self.ui.description_label: "task.description",
            self.ui.at_layout_2: "task.at",
            self.ui.due_label: "task.due",

            # Repeatable
            self.ui.repeatable_label: "repeatable.label",
            self.ui.every_label: "repeat.every",
            self.ui.few_days_label: "repeat.how_many_days",
            self.ui.label: "repeat.on_day",

            # Week day buttons
            self.ui.mon: "week.mon",
            self.ui.tue: "week.tue",
            self.ui.wed: "week.wed",
            self.ui.thu: "week.thu",
            self.ui.fri: "week.fri",
            self.ui.sat: "week.sat",
            self.ui.sun: "week.sun",

            # Task properties
            self.ui.diff_label: "difficulty.label",
            self.ui.categ_label: "category.label",

            # Submit
            self.ui.submit_button: "popup.done",
        }

        for widget, key in translations_map.items():
            widget.setText(lang[key])

        combos_map = {

            self.ui.diff_box: {
                lang['difficulty.very_easy']: 'very_easy',
                lang['difficulty.easy']: 'easy',
                lang['difficulty.medium']: 'medium',
                lang['difficulty.hard']: 'hard',
            },

            self.ui.difficulty_combobox: {
                lang['category.sport']: 'sport',
                lang['category.education']: 'education',
                lang['category.social']: 'social',
                lang['category.chores']: 'chores',
                lang['category.meal']: 'meal',
                lang['category.hygiene']: 'hygiene',
                lang['category.job']: 'job',
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

        }

        for combo in combos_map:
            combo.blockSignals(True)
            combo.clear()
            for item, data in combos_map[combo].items():
                combo.addItem(item, data)
            combo.blockSignals(False)
popup = Popup()
signals.show_add_task_popup.connect(lambda: popup.show_add_task_popup())
