from dotenv import load_dotenv
import os

load_dotenv()

#windows
main_ui = os.getenv('main_ui')
popup_ui = os.getenv('popup_ui')

#widgets
task_widget_ui = os.getenv('task_widget_ui')
task_step_ui = os.getenv('task_step_ui')

#user
user = os.getenv('user')