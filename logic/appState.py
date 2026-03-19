import datetime
from data.init_db import conn, cursor
from config.env_loader import user
from logic.core import calculate_next_occurrence


class AppState:
    def __init__(self):
        self.cur_task = None
        self.cur_date = datetime.datetime.now(datetime.timezone.utc).timestamp()

        self.task_ammo = 0
        self.tasks = {}
        self.dates = []

    def upload_tasks_info(self):
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
            description                    
        FROM users WHERE user=? ''', (user,))

        data = cursor.fetchall()

        if data:
            for task in data:
                self.tasks[task[0]] = {
                    'taskWidget': None,
                    'taskNo': self.task_ammo,
                    'difficulty': task[4],
                    'category': task[5],
                    'description': task[11],
                    'completed':task[6],
                    'duration':[task[2], task[3]],
                    'taskDate' : {
                        'date' : task[1],
                        'page' : None
                    },
                    'taskSteps': {
                        'steps' : {},
                        'page' : None
                    },
                    'repeatable': {
                        'is_repeatable' : task[7],
                        'next_occurrence': None, #calculate_next_occur
                        'rep_option' : task[8],
                        'rep_vals' : task[9].split(' ')
                                 }
                                 }

                for step in task[10].split('@')[:-1]:
                    step_name, step_completed = step[:-1], int(step[-1])
                    self.tasks[task[0]]['taskSteps']['steps'][step_name] = step_completed

                if task[7]:
                    self.tasks[task[0]]['repeatable']['next_occurrence'] = calculate_next_occurrence(
                                                                            task[8],
                                                                            self.tasks[task[0]]['repeatable']['rep_vals'],
                                                                            None)

                self.task_ammo += 1

        print(self.tasks)

state = AppState()