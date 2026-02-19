

def show_add_task_popup():
    global popup
    popup = None
    popup = loader.load(popup_ui, None)

    #popup.setStretch(1,1,1,1,1,1,1,1)

    popup.repeatable_widget.setVisible(False)
    popup.every_stack.setCurrentWidget(popup.day)
    popup.every_stack.setVisible(False)

    popup.repeatable_toggle = AnimatedToggle.AnimatedToggle(popup)
    popup.repeatable_layout.replaceWidget(popup.rep_switch, popup.repeatable_toggle)
    popup.repeatable_toggle.toggled.connect(set_popup_repeatable_menu)

    popup.submit_button.clicked.connect(submit)

    popup.every_box.currentTextChanged.connect(set_popup_every_stack)

    popup.show()

def set_popup_repeatable_menu():
    global popup
    popup.repeatable_widget.setVisible(popup.repeatable_toggle._checked)

def set_popup_every_stack():
    global popup
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

def submit():
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
        set_mw_every_stack()
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
    tasks[_task_name] = {'taskWidget': task,
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

    set_task_info(_task_name, _task_description, _task_difficulty, _task_category)

    task_ammo+=1

    popup.close()

    #add repeatable
