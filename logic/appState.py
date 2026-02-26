import datetime

class AppState:
    def __init__(self):
        self.cur_task = None
        self.cur_date = datetime.datetime.now(datetime.timezone.utc).timestamp()

        self.task_ammo = 0
        self.tasks = {}
        self.dates = []


state = AppState()