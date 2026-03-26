import datetime
from data.init_db import conn, cursor
from config.env_loader import user
from logic.core import calculate_next_occurrence


class AppState:
    def __init__(self):
        self.cur_task = 0
        self.cur_date = datetime.datetime.now(datetime.timezone.utc).timestamp()

        self.task_ammo = 0
        self.tasks = {}
        self.dates = []

    def print_tasks(self):
        for key in self.tasks:
            print(key)
            for sub_key in self.tasks[key]:
                print(f'\t{sub_key} : {self.tasks[key][sub_key]}')
state = AppState()