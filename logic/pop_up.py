import datetime

from PySide6.QtUiTools import QUiLoader

#variables
from config.env_loader import popup_ui, user
from logic.appState import state

#funcs
from logic.core import convert_qtTime_str, calculate_next_occurrence
from logic.signalHub import signals

#instances
from data.init_db import conn, cursor
from logic.mainWindow import mw
from logic.tasks import Task

class Popup():
    def __init__(self):
        self.ui = None
        self.ui = QUiLoader().load(popup_ui, None)

        from ui.widgets.toggle import AnimatedToggle

        self.ui.repeatable_toggle = AnimatedToggle(self.ui)
        self.ui.repeatable_layout.replaceWidget(self.ui.rep_switch, self.ui.repeatable_toggle)
        self.ui.repeatable_toggle.toggled.connect(self.set_popup_repeatable_menu)

        self.ui.submit_button.clicked.connect(self.submit)

        self.ui.every_box.currentTextChanged.connect(self.set_popup_every_stack)

        #signals.show_add_task_self.ui.connect(lambda :self.show_add_task_popup())
        #self.show_add_task_popup()

    def show_add_task_popup(self):
        print('show_add_task_popup')
        self.ui.repeatable_widget.setVisible(False)
        self.ui.every_stack.setCurrentWidget(self.ui.day)
        self.ui.every_stack.setVisible(False)

        self.ui.show()

    def set_popup_repeatable_menu(self):
        self.ui.repeatable_widget.setVisible(self.ui.repeatable_toggle._checked)

    def set_popup_every_stack(self):
        cur_option = self.ui.every_box.currentText()

        self.ui.every_stack.setVisible(True)
        if cur_option == 'Few Days':
            self.ui.every_stack.setCurrentWidget(self.ui.few_days)

        elif cur_option == 'Week':
            self.ui.every_stack.setCurrentWidget(self.ui.week)

        elif cur_option == 'Mounth':
            self.ui.every_stack.setCurrentWidget(self.ui.mounth)

        elif cur_option == 'Year':
            self.ui.every_stack.setCurrentWidget(self.ui.year)

        elif cur_option == 'Day':
            self.ui.every_stack.setCurrentWidget(mw.day)
            self.ui.every_stack.setVisible(False)

    def submit(self):

        _task_name = self.ui.name_edit.text()
        state.cur_task = _task_name
        _task_repeatable = self.ui.repeatable_toggle._checked
        if _task_name == '':
            _task_name = f"Task #{state.task_ammo}"

        _task_description = self.ui.description_edit.toPlainText()
        _task_difficulty = self.ui.diff_box.currentText()
        _task_category= self.ui.difficulty_combobox.currentText() # rename it pls

        start_time = convert_qtTime_str(self.ui.at_timeedit.time())
        end_time = convert_qtTime_str(self.ui.due_timeedit.time())

        cur_time_in = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

        next_occurrence = rep_option = rep_vals = None
        if _task_repeatable:
            mw.ui.repeatable_set_widget.setVisible(True)

            rep_option = self.ui.every_box.currentIndex()
            next_occurrence, rep_vals = (calculate_next_occurrence(
                self.ui.every_box.currentText(),
                self.ui.at_timeedit.time(),
                popup
            ))
            mw.ui.every_box.setCurrentIndex(self.ui.every_box.currentIndex())
            mw.funcs.set_mw_every_stack(rep_vals)
        else:
            if mw.ui.repeatable_toggle._checked:
                mw.ui.repeatable_toggle.on_click()
            mw.ui.repeatable_set_widget.setVisible(False)

        #cursor.execute("""
        #INSERT INTO users
        #(user, taskName, start_time, end_time, difficulty, category, completed, repeatable,next_occurrence,task_steps)
        #VALUES (?,?,?,?,?,?,?,?,?,?)""",
        #(user,_task_name,start_time,end_time,_task_difficulty,_task_category,0,_task_repeatable,next_occurrence,''))
        #conn.commit() #<-----------IMPORTANT (off for test cases)

        task = Task(_task_name, _task_description, _task_difficulty, _task_category, start_time, end_time, parent=mw.ui.tasks_scrollwidget)
        state.tasks[_task_name] = {'taskWidget': task,
                             'taskNo': state.task_ammo,
                             'completed':False,
                             'duration':[self.ui.at_timeedit.time(), self.ui.due_timeedit.time()],
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

        state.task_ammo+=1

        self.ui.close()

        #add repeatable
print("signals id:", id(signals))
popup = Popup()
#signals.show_add_task_popup.connect(lambda : print('eee'))
signals.show_add_task_popup.connect(lambda: popup.show_add_task_popup())
#signals.show_add_task_popup.connect(lambda : print('eeee'))
