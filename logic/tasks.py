import datetime

from PySide6.QtCore import QEvent
from PySide6.QtUiTools import QUiLoader

from config.env_loader import task_widget_ui

class Task():
    def __init__(self,name, description, difficulty, category, repeatable = 0,parent = None):
        super().__init__()
        global mw, cur_task

        cur_task = name

        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.category = category

        self.task = QUiLoader.load(task_widget_ui,None)

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

