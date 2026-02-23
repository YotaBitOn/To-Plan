import datetime

from PySide6.QtUiTools import QUiLoader

#variables
from config.env_loader import popup_ui, user
from logic.appState import state

#funcs
from logic.core import convert_qtTime_str, calculate_next_occurrence

#instances
from data.init_db import conn, cursor
from logic.mainWindow import mw
from logic.tasks import Task

class Popup():
    def __init__(self):
        self.ui = None
        self.ui = QUiLoader().load(popup_ui, None)

        self.show_add_task_popup()

    def show_add_task_popup(self):
        self.ui.repeatable_widget.setVisible(False)
        self.ui.every_stack.setCurrentWidget(self.ui.day)
        self.ui.every_stack.setVisible(False)

        from ui.widgets.toggle import AnimatedToggle

        self.ui.repeatable_toggle = AnimatedToggle(self.ui)
        self.ui.repeatable_layout.replaceWidget(self.ui.rep_switch, self.ui.repeatable_toggle)
        self.ui.repeatable_toggle.toggled.connect(self.set_popup_repeatable_menu)

        self.ui.submit_button.clicked.connect(self.submit)

        self.ui.every_box.currentTextChanged.connect(self.set_popup_every_stack)

        self.ui.show()

    def set_popup_repeatable_menu(self):
        popup.repeatable_widget.setVisible(popup.repeatable_toggle._checked)

    def set_popup_every_stack(self):
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

    def submit(self):
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
            mw.funcs.set_mw_every_stack()
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
        state.tasks[_task_name] = {'taskWidget': task,
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

        mw.funcs.set_task_info(_task_name, _task_description, _task_difficulty, _task_category)

        task_ammo+=1

        popup.close()

        #add repeatable

popup = Popup()