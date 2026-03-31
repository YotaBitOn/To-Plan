import datetime

from config.env_loader import cur_theme

class AppState:
    def __init__(self):
        self.cur_task = 0
        self.task_ammo = 0
        self.tasks = {}

        self.cur_date = datetime.datetime.now(datetime.timezone.utc).timestamp()
        self.dates = []

    def print_tasks(self):
        for key in self.tasks:
            print(key)
            for sub_key in self.tasks[key]:
                print(f'\t{sub_key} : {self.tasks[key][sub_key]}')
state = AppState()