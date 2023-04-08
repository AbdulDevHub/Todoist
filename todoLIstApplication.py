"""
Title: To-Do List Application
Description: An Intuitive App To Manage Tasks And Organize Your Life
Authors: Abdul Khan & Uzair
Last Modified: April 06, 2023
"""

# ==============================================
#                Program Imports
# ==============================================

# ============== Built-In Module & Package Imports ==============
import os
import json
import pickle
import re
import tkinter as tk
from datetime import datetime
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.font import Font

# ============== Personal Class Import ==============
from progressTracker import ProgressTracker

# ============== Global Constant Variables ==============
WHITE_COLOR = "WHITE"  # Can be used to set window(s) bg color
RED_COLOR = "#F57878"
LIGHT_GREEN_COLOR = "#94FFA6"
BLUE_COLOR = "#7DE0FF"
GREY_COLOR = "#555555"
YELLOW_COLOR = "#F5FF83"

# ============== Global Non-Constant Variables ==============
tasks = []  # Contains all current tasks
progressTracker = []  # Stores user actions in manging tasks
filteredTasks = []  # Search bar filtered task list
tasksListFlipped = False

topDoneIndex = len(tasks)  # Topmost completed task
bottomPriorityIndex = 0  # Bottom most prioritized task

# ==============================================
#                 Functions
# ==============================================

# ============== Import & Export Application Save Files ==============

def insertItem(task, index):
    """ Formats new task item & inserts into task list box """

    # Only adds task name, description, and creation date to task list box view
    name = task['name']
    description = task['description']

    copyDescription = description[:]
    possibleLen = 33 - len(name)
    dateMade = datetime.now()

    # Truncate summary if necessary and add ellipsis
    if len(copyDescription) > possibleLen:
        copyDescription = copyDescription[:possibleLen] + "... "
        numSpaces = " " * 0
    else:
        totalLength = len(name) + len(copyDescription)
        numSpaces = " " * (37 - totalLength)

    # Insert formatted string into listbox
    tasksPanelView.insert(index, f"  {name}: {copyDescription} {numSpaces} {dateMade.strftime('%d/%m/%y')}")

    # Set background color to indicate whether task is done or has priority
    if task["done"]: tasksPanelView.itemconfig(index, {'bg': LIGHT_GREEN_COLOR})
    elif task["priority"]: tasksPanelView.itemconfig(index, {'bg': YELLOW_COLOR})


def loadSavedFile():
    """ Loads file saved content back into global variables and lists """

    # If application was used previously or saved file is opened by user
    if os.path.exists('../persistentSave.pkl'):
        if os.path.getsize('../persistentSave.pkl') > 0:
            with open('../persistentSave.pkl', 'rb') as f:
                data = pickle.load(f)

            # Update application status with file saved status
            global tasks
            tasks.clear()
            tasks.extend(data["tasks"])

            global progressTracker
            progressTracker.clear()
            progressTracker.extend(data["progressTracker"])

            global tasksPanelView
            tasksPanelView.delete(0, tk.END)

            global tasksListFlipped
            tasksListFlipped = data["tasksListFlipped"]

            global topDoneIndex
            topDoneIndex = data["topDoneIndex"]

            global bottomPriorityIndex
            bottomPriorityIndex = data["bottomPriorityIndex"]

            # Show new status of application and task panel view
            for index, task in enumerate(tasks): insertItem(task, index)


def updatePersistentFile():
    """ Save primary status of application to persistent pickle file """
    with open('../persistentSave.pkl', 'wb') as f:
        data = {"tasks": tasks, "progressTracker": progressTracker,
                "tasksListFlipped": tasksListFlipped, "bottomPriorityIndex": bottomPriorityIndex,
                "topDoneIndex": topDoneIndex}
        pickle.dump(data, f)


def clearAll():
    """ Reset application to default status """

    global topDoneIndex
    topDoneIndex = 0

    global bottomPriorityIndex
    bottomPriorityIndex = 0

    global progressTracker
    progressTracker = []

    global tasks
    tasks = []

    global tasksPanelView
    tasksPanelView.delete(0, END)

    global filteredTasks
    filteredTasks = []

    global tasksListFlipped
    tasksListFlipped = False

    # Also deletes the persistent file
    if os.path.exists('../persistentSave.pkl'): os.remove(
        '../persistentSave.pkl')


def saveTaskList():
    """
    Saves task list as a json file to allow easier
    readability & computer transferences
    """

    filePath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if filePath:
        with open(filePath, 'w') as f:

            # Convert datetime objects to strings
            for task in tasks: task["creation date"] = task["creation date"].strftime('%Y-%m-%d %H:%M:%S')

            # Save application status variables to file
            data = {"tasks": tasks, "progressTracker": progressTracker,
                    "tasksListFlipped": tasksListFlipped, "bottomPriorityIndex": bottomPriorityIndex,
                    "topDoneIndex": topDoneIndex}
            json.dump(data, f)

        # Alert user of a successful save
        messagebox.showinfo("Save To-Do List", "Your To-Do List Was Successfully Saved")


def openTaskList():
    """ Open and load user selected json saved task list to application """

    filePath = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if filePath:
        with open(filePath, 'r') as f:
            data = json.load(f)

        global tasksListFlipped
        tasksListFlipped = data["tasksListFlipped"]

        global topDoneIndex
        topDoneIndex = data["topDoneIndex"]

        global bottomPriorityIndex
        bottomPriorityIndex = data["bottomPriorityIndex"]

        global progressTracker
        progressTracker.clear()
        progressTracker.extend(data["progressTracker"])

        global tasks
        tasks.clear()
        tasks.extend(data["tasks"])

        # Convert strings back to datetime objects
        for task in tasks: task["creation date"] = datetime.strptime(task["creation date"], '%Y-%m-%d %H:%M:%S')

        # Load saved task list to application & alert user
        updatePersistentFile()
        loadSavedFile()
        messagebox.showinfo("Open To-Do List", "Your To-Do List Was Opened successfully")


def onClosing():
    """ Save application status for next time window is reopened """
    updatePersistentFile()
    root.destroy()

# ============== Related To Main Window’s Bottom Buttons ==============

def priorTaskOccurrences(selectedTaskIndex, selectedTaskValue):
    """
    Counts and returns the number of times a task with exact
    name was found before currently selected task
    """
    count = 0
    for i in range(selectedTaskIndex):
        currentTaskValue = tasksPanelView.get(i)[2:2 + len(selectedTaskValue)]
        if currentTaskValue == selectedTaskValue: count += 1
    return count


def addNewTask():
    """ Opens a new window that lets you enter and save info for new task """

    def submit():
        """ Saves user entered values & updates main window's status """

        # Retrieve user inputs from entry widgets and check boxes
        name = summaryEntry.get()
        # If no task name entered
        if name == "Limit To 25 Characters" or name == "": name = "Untitled"

        # Ensure correct date format entered for deadline before saving user inputs
        deadline = deadlineEntry.get()
        deadlinePattern = re.compile(r'\d{4}/\d{1,2}/\d{1,2}/\d{1,2}:\d{1,2}')
        if deadline == "" or deadlinePattern.fullmatch(deadline):
            # Save user inputs to tasks list
            categories = [category for category, wasSelected in categoryVars.items() if wasSelected.get()]
            creationDate = datetime.now()
            summary = descriptionEntry.get("1.0", "end-1c")
            done = False
            prioritize = False
            reminder = None
            global topDoneIndex

            tasks.insert(topDoneIndex, {
                "order": topDoneIndex,
                "name": name,
                "deadline": deadline,
                "category": categories,
                "creation date": creationDate,
                "description": summary,
                "done": done,
                "priority": prioritize,
                "reminder": reminder
            })

            # Update remaining main window's status variables
            insertItem(tasks[topDoneIndex], topDoneIndex)
            progressTracker.append(["add", datetime.now().strftime('%m')])
            topDoneIndex += 1
            top.destroy()
        else: messagebox.showerror("Error", "The deadline isn't in the correct format ('YYYY/M/D/H:M').")

    # New temporary add task window
    top = Toplevel()
    top.title("Add Task")
    top.geometry("400x460")
    top.configure(bg=WHITE_COLOR)

    # Add top-padding to task window
    spacer = Label(top, bg=WHITE_COLOR)
    spacer.pack(pady=5)
    entryFrame = Frame(top, bg=WHITE_COLOR)

    # Don't let user type in name longer than 25 characters
    def validateText(text): return len(text) <= 25
    vcmd = (top.register(validateText), '%P')

    summaryLabel = Label(entryFrame, text="Task Summary:", bg=WHITE_COLOR)
    summaryLabel.grid(row=0, column=0, pady=10)
    summaryEntry = Entry(entryFrame, bg=BLUE_COLOR, fg=GREY_COLOR, validate="key", validatecommand=vcmd)
    summaryEntry.insert(0, "Limit To 25 Characters")
    summaryEntry.grid(row=0, column=1, pady=10)

    def summaryOnEntryClick(event):
        """ Makes summary entry empty to let user type their input """
        if summaryEntry.get() == "Limit To 25 Characters":
            summaryEntry.delete(0, tk.END)
            summaryEntry.insert(0, '')
            summaryEntry.config(fg="black")

    def summaryOnFocusOut(event):
        """
        Makes summary entry showcase 'Limit To 25 Characters' if
        user hasn't entered a task summary
        """
        if summaryEntry.get() == '':
            summaryEntry.insert(0, "Limit To 25 Characters")
            summaryEntry.config(fg=GREY_COLOR)

    # Actively updates summary entry as user types or leaves
    summaryEntry.bind('<FocusIn>', summaryOnEntryClick)
    summaryEntry.bind('<FocusOut>', summaryOnFocusOut)

    deadlineLabel = Label(entryFrame, text="Deadline (Y/M/D/H:M):  ", bg=WHITE_COLOR)
    deadlineLabel.grid(row=1, column=0, pady=10)
    deadlineEntry = Entry(entryFrame, bg=BLUE_COLOR)
    deadlineEntry.grid(row=1, column=1, pady=10)

    entryFrame.pack()

    categoryLabel = Label(top, text="Category:", bg=WHITE_COLOR)
    categoryLabel.pack(pady=20)
    categoryOptions = ["Work", "Personal", "Health", "Social",
                        "Education", "Financial", "Hobby", "Other"]
    categoryVars = {category: IntVar() for category in categoryOptions}

    checkbuttonFrame = Frame(top, bg=WHITE_COLOR)
    for i, (category, var) in enumerate(categoryVars.items()):
        checkbutton = Checkbutton(checkbuttonFrame, text=category, variable=var,
                                  bg=WHITE_COLOR, selectcolor=BLUE_COLOR)
        checkbutton.grid(row=i//4, column=i%4)
    checkbuttonFrame.pack()

    descriptionLabel = Label(top, text="Description:", bg=WHITE_COLOR)
    descriptionLabel.pack(pady=15)
    descriptionEntry = Text(top, width=40, height=5, bg=BLUE_COLOR)
    descriptionEntry.pack(pady=10)

    submitButton = Button(top, text="Submit", command=submit, bg=LIGHT_GREEN_COLOR)
    submitButton.pack(pady=20)


def deleteTask():
    """ Deletes selected task from list of tasks """

    global topDoneIndex
    global bottomPriorityIndex

    # If something is selected in task list panel, delete it
    selection = tasksPanelView.curselection()
    if selection:

        # Find where that selected item is in the task list
        # This approach is useful when using the search bar to delete
        index = selection[0]
        value = tasksPanelView.get(index)
        value = value[2:value.rfind(':')]
        occurrence = priorTaskOccurrences(index, value)

        taskIndex = None
        count = 0
        for item in tasks:
            if item["name"] == value:
                if count == occurrence:
                    taskIndex = tasks.index(item)  # Found task index in task list
                    tasks.remove(item)  # Remove task from task list
                    break
                count += 1

        # Update other application status variables
        tasksPanelView.delete(index)
        progressTracker.append(["delete", datetime.now().strftime('%m')])
        if index <= topDoneIndex: topDoneIndex -= 1
        if index < bottomPriorityIndex > 0: bottomPriorityIndex -= 1
        for i in range(taskIndex, len(tasks)): tasks[i]["order"] -= 1

        # If all tasks are deleted
        if not tasks:
            topDoneIndex = len(tasks)
            bottomPriorityIndex = 0


def markTaskDoneOrUndone():
    """ Marks or unmarks selected task from list of tasks as done """

    global topDoneIndex
    global bottomPriorityIndex

    # If something is selected in task list panel, mark/unmark done
    selection = tasksPanelView.curselection()
    if selection:

        # Don't let user mark/unmark done while using search bar
        searchTerm = entryVar.get().lower()
        if searchTerm != "" and searchTerm != "search":
            markDoneOrUndoneButton.config(text="Mark Done", bg=LIGHT_GREEN_COLOR)
            prioritizeOrUnprioritizeButton.config(text="Prioritize", bg=LIGHT_GREEN_COLOR)
            messagebox.showerror("Error", "This Action Isn't Allowed While Searching.")
            return

        # Don't let user mark/unmark done while list isn't sorted properly
        if sortVar.get().lower() != "default":
            messagebox.showerror("Error", '"Sort By" Must be Set To Default.')
            return
        if tasksListFlipped:
            messagebox.showerror("Error", "Tasks Must Not Be Flipped.")
            return

        # If selected task is prioritized, unprioritize it
        index = selection[0]
        if tasks[index]["priority"]:
            prioritizeOrUnprioritizeTask()
            index = bottomPriorityIndex

        task = tasks.pop(index)
        task["done"] = not task["done"]

        # Mark selected task as done and move to bottom of task list
        if task["done"]:
            topDoneIndex -= 1
            tasks.append(task)
            tasksPanelView.delete(index)

            # Update task panel & give task green color to indicate it's done
            insertItem(task, END)
            tasksPanelView.itemconfig(END, {'bg': LIGHT_GREEN_COLOR})

            # Update other application status variables
            progressTracker.append(["done", datetime.now().strftime('%m')])
            for i in range(index, len(tasks)): tasks[i]["order"] -= 1
            tasks[len(tasks) - 1]["order"] = len(tasks) - 1

        # Mark selected task as not done & move it above highest done task
        else:
            tasks.insert(topDoneIndex, task)
            tasksPanelView.delete(index)
            insertItem(task, topDoneIndex)

            # Update other application status variables
            progressTracker.append(["undone", datetime.now().strftime('%m')])
            topDoneIndex += 1
            for i in range(topDoneIndex, len(tasks)): tasks[i]["order"] += 1
            tasks[topDoneIndex - 1]["order"] = topDoneIndex - 1

            # Return to default statuses
            markTaskDoneOrUndone.config(text="Mark Done", bg=LIGHT_GREEN_COLOR)
        tasksPanelView.selection_clear(0, END)


def prioritizeOrUnprioritizeTask():
    """ Prioritizes or unprioritizes selected task """

    global bottomPriorityIndex
    global topDoneIndex

    # If something is selected in task list panel, prioritize/unprioritize it
    selection = tasksPanelView.curselection()
    if selection:

        # Don't let user prioritize/unprioritize while using search bar
        searchTerm = entryVar.get().lower()
        if searchTerm != "" and searchTerm != "search":
            markDoneOrUndoneButton.config(text="Mark Done", bg=LIGHT_GREEN_COLOR)
            prioritizeOrUnprioritizeButton.config(text="Prioritize", bg=LIGHT_GREEN_COLOR)
            messagebox.showerror("Error", "This Action Isn't Allowed While Searching.")
            return

        # Don't let user prioritize/unprioritize while list isn't sorted properly
        if sortVar.get().lower() != "default":
            messagebox.showerror("Error", '"Sort By" Must be Set To Default.')
            return
        if tasksListFlipped:
            messagebox.showerror("Error", "Tasks Must Not Be Flipped.")
            return

        # If selected task is marked as done, unmark it
        index = selection[0]
        if tasks[index]["done"]:
            markTaskDoneOrUndone()
            index = topDoneIndex - 1

        task = tasks.pop(index)
        task["priority"] = not task["priority"]

        # Mark selected task as priority and move to top of task list
        if task["priority"]:
            bottomPriorityIndex += 1
            tasks.insert(0, task)
            tasksPanelView.delete(index)

            # Update task panel & give task yellow color to indicate it's a priority
            insertItem(task, 0)
            tasksPanelView.itemconfig(0, {'bg': YELLOW_COLOR})

            # Update other application status variables
            for i in range(1, index + 1): tasks[i]["order"] += 1
            tasks[0]["order"] = 0

        # Mark selected task as normal & move it below lowest priority task
        else:
            bottomPriorityIndex -= 1
            tasks.insert(bottomPriorityIndex, task)
            tasksPanelView.delete(index)
            insertItem(task, bottomPriorityIndex)

            # Update other application status variables
            for i in range(bottomPriorityIndex + 1, len(tasks)): tasks[i]["order"] -= 1
            tasks[bottomPriorityIndex]["order"] = bottomPriorityIndex

            # Return to default statuses
            prioritizeOrUnprioritizeButton.config(text="Prioritize", bg=LIGHT_GREEN_COLOR)
        tasksPanelView.selection_clear(0, END)


def setTaskReminder():
    """ Set a alarm-based reminder for selected task """

    # If something is selected in task list panel, set a reminder for it
    selection = tasksPanelView.curselection()
    if selection:

        # Only need task name
        index = selection[0]
        value = tasksPanelView.get(index)
        taskName = value[2:value.rfind(':')]

        def setReminder():
            """ Sets reminder for user selected task """

            # Ensure imputed reminder time is entered correctly
            reminderTime = reminderEntry.get()
            try:
                reminderDatetime = datetime.strptime(reminderTime, '%Y-%m-%d %H:%M')

                # Ensure inputted reminder time occurs in future
                currentTime = datetime.now()
                timeDifference = (reminderDatetime - currentTime).total_seconds() * 1000
                if timeDifference > 0:
                    root.after(int(timeDifference), showReminder)
                    reminderWindow.destroy()
                else: messagebox.showerror("Error", "The reminder time must be in the future.")
            except ValueError: messagebox.showerror("Error", "Invalid format. Please enter as 'YYYY-MM-DD HH:MM'.")

        def showReminder():
            """ Create reminder window when inputted reminder time arrives """
            reminderAlertWindow = Toplevel()
            reminderAlertWindow.title(f"Reminder: {taskName.title()}")
            reminderAlertWindow.geometry("400x100")
            reminderAlertWindow.configure(bg=WHITE_COLOR)
            Label(reminderAlertWindow, text=f'It\'s Time For "{taskName.title()}"!!!', bg=WHITE_COLOR).pack(pady=10)

            def dismiss(): reminderAlertWindow.destroy()
            def snooze():
                reminderAlertWindow.destroy()
                root.after(300000, showReminder)  # 5 minute snooze

            buttonFrame = Frame(reminderAlertWindow, bg=WHITE_COLOR)
            Button(buttonFrame, text="Snooze", command=snooze, bg=YELLOW_COLOR).pack(side=LEFT, padx=5)
            Button(buttonFrame, text="Dismiss", command=dismiss, bg=RED_COLOR).pack(side=LEFT, padx=5)
            buttonFrame.pack(pady=10)

        # New temporary set task reminder window
        reminderWindow = Toplevel()
        reminderWindow.title("Set Reminder")
        reminderWindow.geometry("400x180")
        reminderWindow.configure(bg=WHITE_COLOR)
        Label(reminderWindow, text=f"Task: {taskName}", bg=WHITE_COLOR).pack(pady=10)
        Label(reminderWindow, text="Enter Reminder Date. This Field Is Required.", bg=WHITE_COLOR).pack(pady=10)

        formatFrame = Frame(reminderWindow, bg=WHITE_COLOR)
        Label(formatFrame, text="Format: YYYY-MM-DD HH:MM", bg=WHITE_COLOR).pack(side=LEFT, padx=5)
        reminderEntry = Entry(formatFrame, bg=BLUE_COLOR)
        reminderEntry.pack(side=LEFT, padx=5)
        formatFrame.pack(pady=10)

        buttonFrame = Frame(reminderWindow, bg=WHITE_COLOR)
        Button(buttonFrame, text="Set Reminder", command=setReminder, bg=LIGHT_GREEN_COLOR).pack(side=LEFT, padx=5)
        Button(buttonFrame, text="Cancel", command=reminderWindow.destroy, bg=RED_COLOR).pack(side=LEFT, padx=5)
        buttonFrame.pack(pady=10)
    else: messagebox.showerror("Error", "Please select a task from the list.")

""" Creates task progress graph """
def viewProgress(): ProgressTracker(progressTracker).show()

# ============== Related To Main Window’s Center & Surrounding Area ==============

def showAndEditInfo(event):
    """ Opens a new window that lets you view and update task info """

    # If something is selected in task list panel, find it task list index
    # This approach is useful when using the search bar to view/edit tasks
    selection = tasksPanelView.curselection()
    if not selection: return
    index = selection[0]
    value = tasksPanelView.get(index)
    value = value[2:value.rfind(':')]
    occurrence = priorTaskOccurrences(index, value)

    task = None
    count = 0
    for item in tasks:
        if item["name"] == value:
            if count == occurrence:
                task = item  # Found task in task list
                break
            count += 1

    def save():
        """ Updates user entered values & main window's status """

        # Retrieve user inputs from entry widgets and check boxes
        summary = summaryEntry.get()
        # If no task name entered
        if summary == "Limit To 25 Characters" or summary == "": summary = "Untitled"

        # Ensure correct date format entered for deadline before updating user inputs
        deadline = deadlineEntry.get()
        deadlinePattern = re.compile(r'\d{4}/\d{1,2}/\d{1,2}/\d{1,2}:\d{1,2}')
        if deadline == "" or deadlinePattern.fullmatch(deadline):
            # Update user selected task with new inputs
            task["name"] = summary
            task["deadline"] = deadlineEntry.get()
            task["category"] = [category for category, var in categoryVars.items() if var.get()]
            task["description"] = descriptionEntry.get("1.0", "end-1c")

            # Update task panel view
            tasksPanelView.delete(index)
            insertItem(task, index)
            top.destroy()
        else: messagebox.showerror("Error", "The deadline isn't in the correct format ('YYYY/M/D/H:M').")

    # New temporary view/edit task window
    top = Toplevel()
    top.title("Edit Task")
    top.geometry("400x500")
    top.configure(bg=WHITE_COLOR)

    # Add top-padding to task window
    spacer = Label(top, bg=WHITE_COLOR)
    spacer.pack(pady=5)
    entryFrame = Frame(top, bg=WHITE_COLOR)

    # Don't let user type in name longer than 25 characters
    def validateText(text): return len(text) <= 25
    vcmd = (top.register(validateText), '%P')

    # Update summary entry based on pre-existing summary value
    summaryContent = task["name"]
    summaryEntryColor = "black"
    if summaryContent == "Untitled":
        summaryEntryColor = GREY_COLOR
        summaryContent = "Limit To 25 Characters"

    summaryLabel = Label(entryFrame, text="Task Summary:", bg=WHITE_COLOR)
    summaryLabel.grid(row=0, column=0, pady=10)
    summaryEntry = Entry(entryFrame, bg=BLUE_COLOR, fg=summaryEntryColor, validate="key", validatecommand=vcmd)
    summaryEntry.grid(row=0, column=1, pady=10)
    summaryEntry.insert(0, summaryContent)  # Insert pre-existing summary value

    def summaryOnEntryClick(event):
        """ Makes summary entry empty to let user type their input """
        if summaryEntry.get() == "Limit To 25 Characters":
            summaryEntry.delete(0, tk.END)
            summaryEntry.insert(0, '')
            summaryEntry.config(fg="black")

    def summaryOnFocusOut(event):
        """
        Makes summary entry showcase 'Limit To 25 Characters' if
        user hasn't entered a task summary
        """
        if summaryEntry.get() == '':
            summaryEntry.insert(0, "Limit To 25 Characters")
            summaryEntry.config(fg=GREY_COLOR)

    # Actively updates summary entry as user types or leaves
    summaryEntry.bind('<FocusIn>', summaryOnEntryClick)
    summaryEntry.bind('<FocusOut>', summaryOnFocusOut)

    deadlineLabel = Label(entryFrame, text="Deadline (Y/M/D/H:M):  ", bg=WHITE_COLOR)
    deadlineLabel.grid(row=1, column=0, pady=10)
    deadlineEntry = Entry(entryFrame, bg=BLUE_COLOR)
    deadlineEntry.grid(row=1, column=1, pady=10)
    deadlineEntry.insert(0, task["deadline"])  # Insert pre-existing deadline value

    entryFrame.pack()

    categoryLabel = Label(top, text="Category:", bg=WHITE_COLOR)
    categoryLabel.pack(pady=20)
    categoryOptions = ["Work", "Personal", "Health", "Social",
                        "Education", "Financial", "Hobby", "Other"]
    # Insert pre-existing category values
    categoryVars = {category: IntVar(value=int(category in task["category"])) for category in categoryOptions}

    checkbuttonFrame = Frame(top, bg=WHITE_COLOR)
    for i, (category, var) in enumerate(categoryVars.items()):
        checkbutton = Checkbutton(checkbuttonFrame, text=category, variable=var,
                                  bg=WHITE_COLOR, selectcolor=BLUE_COLOR)
        checkbutton.grid(row=i//4, column=i%4)
    checkbuttonFrame.pack()

    descriptionLabel = Label(top, text="Description:", bg=WHITE_COLOR)
    descriptionLabel.pack(pady=15)
    descriptionEntry = Text(top, width=40, height=5, bg=BLUE_COLOR)
    descriptionEntry.insert("end", task["description"])  # Insert pre-existing description value
    descriptionEntry.pack(pady=10)

    # Insert pre-existing creation date value
    creationDate = task['creation date'].strftime('%Y/%m/%d/%H:%M')
    creationDateLabel = Label(top, text=f"Creation Date: {creationDate}", bg=WHITE_COLOR)
    creationDateLabel.pack(pady=15)

    saveButton = Button(top, text="Save Task", command=save, bg=LIGHT_GREEN_COLOR)
    saveButton.pack(pady=10)


def onWindowClick(event):
    """ Removes focus from search bar & unselects tasks when window clicked """

    # Ensures typing and clicking of buttons is still possible
    if event.widget != entry \
            and event.widget != tasksPanelView \
            and event.widget != markDoneOrUndoneButton \
            and event.widget != prioritizeOrUnprioritizeButton \
            and event.widget != deleteTaskButton \
            and event.widget != setReminderButton:
        root.focus()
        tasksPanelView.selection_clear(0, END)

        # Set to default status
        markDoneOrUndoneButton.config(text="Mark Done", bg=LIGHT_GREEN_COLOR)
        prioritizeOrUnprioritizeButton.config(text="Prioritize", bg=LIGHT_GREEN_COLOR)


def taskSelected(event):
    """ Function to update mark done & prioritize buttons based on selected task """

    # If something is selected in task list panel, check priority & done status
    selection = tasksPanelView.curselection()
    if selection:
        # Get selected task
        index = selection[0]
        task = tasks[index]

        # Invert "Mark Done" button's text and color
        if task["done"]: markDoneOrUndoneButton.config(text="Mark Not Done", bg=RED_COLOR)
        else: markDoneOrUndoneButton.config(text="Mark Done", bg=LIGHT_GREEN_COLOR)

        # Invert "Prioritize" button's text and color
        if task["priority"]: prioritizeOrUnprioritizeButton.config(text="De-Prioritize", bg=RED_COLOR)
        else: prioritizeOrUnprioritizeButton.config(text="Prioritize", bg=LIGHT_GREEN_COLOR)


"""
Deselects task when task list panel loses focus. 
Primarily meant for when interacting with buttons and search bar.
"""
def deselectTasks(event): tasksPanelView.selection_clear(0, tk.END)

# ============== Related To Main Window’s Top Area ==============

def searchBarFocusIn(event):
    """ Empty and color in search bar when in use """

    if entry.get() == "Search":
        entry.delete(0, END)
        entry.config(fg="black")

        # Set to default status when using search bar
        markDoneOrUndoneButton.config(text="Mark Done", bg=LIGHT_GREEN_COLOR)
        prioritizeOrUnprioritizeButton.config(text="Prioritize", bg=LIGHT_GREEN_COLOR)


def searchBarFocusOut(event):
    """ Fade out search bar when not in use """

    if entry.get() == "":
        entry.insert(0, "Search")
        entry.config(fg="grey")
        searchTasks()


def searchTasks(*args):
    """ Filters task list based on user search input """

    global filteredTasks
    currentSearchTerm = entryVar.get().lower()
    currentSearchType = (searchTypeVar.get()).lower()
    tasksPanelView.delete(0, END)

    # Filter tasks based on search input and type
    if currentSearchTerm == "" or currentSearchTerm == "search": filteredTasks = tasks  # Not in use search bar shows all tasks
    elif currentSearchType == "category":
        filteredTasks = [task for task in tasks if any(currentSearchTerm in element.lower() for element in task["category"])]
    elif currentSearchType == "creation date":
        filteredTasks = [task for task in tasks if currentSearchTerm in task[currentSearchType].strftime('%Y/%m/%d/%H:%M')]
    else: filteredTasks = [task for task in tasks if currentSearchTerm in task[currentSearchType].lower()]

    # Display all filtered tasks to task list panel
    for task in filteredTasks: insertItem(task, END)


def sortTasks():
    """ Sorts list of tasks based on currently selected sorting option """

    currentSortType = sortVar.get().lower()
    if currentSortType == "name": tasks.sort(key=lambda x: x["name"])
    elif currentSortType == "deadline": tasks.sort(key=lambda x: x["deadline"])
    elif currentSortType == "default": tasks.sort(key=lambda x: x["order"])
    elif currentSortType == "creation date": tasks.sort(key=lambda x: x["creation date"])

    # Displays a sorted & search bar filtered list to task list panel
    tasksPanelView.delete(0, END)
    taskList = tasks.copy()
    if filteredTasks: taskList = [task for task in tasks if task in filteredTasks]
    for task in taskList: insertItem(task, END)


def flipSort():
    """ Reverses the list of tasks """

    global tasksListFlipped
    tasksListFlipped = not tasksListFlipped
    tasks.reverse()
    tasksPanelView.delete(0, END)

    # Displays a flipped & search bar filtered list to task list panel
    taskList = tasks.copy()
    if filteredTasks: taskList = [task for task in tasks if task in filteredTasks]
    for task in taskList: insertItem(task, END)


""" Sorts tasks when sorting option is changed """
def sortOptionChanged(*args): sortTasks()

# ==============================================
#                 Main Window
# ==============================================

root = Tk()
root.configure(background=WHITE_COLOR)
root.title('To-Do List Application')
root.geometry("750x515")

# Meant to contain & center window elements
entryFrame = Frame(root, bg=WHITE_COLOR)
entryFrame.pack(pady=20)

# ============== Search Bar Related Widgets ==============

# Default values for entry and menus
entryVar = StringVar()
searchTypeVar = StringVar(value="Name")
sortVar = StringVar(value="Default")

# List of options for the search type and sorting dropdown menus
searchTypeOptions = ["Name", "Deadline", "Category", "Creation Date", "Description"]
sortOptions = ["Default", "Name", "Deadline", "Creation Date"]

# Search bar
entry = Entry(entryFrame, textvariable=entryVar, font=("Helvetica", 24), bg=BLUE_COLOR, width=25)
entry.grid(row=0, column=0, padx=9)
entry.insert(0, "Search")
entry.config(fg="grey")

# Search type dropdown menu
searchTypeButton = Menubutton(entryFrame, text="Search Type", bg=LIGHT_GREEN_COLOR, relief="raised")
searchTypeButton.grid(row=0, column=2, padx=4)
searchTypeMenu = Menu(searchTypeButton, tearoff=False)
searchTypeButton.config(menu=searchTypeMenu)
for option in searchTypeOptions:  # Add dropdown menu options
    searchTypeMenu.add_radiobutton(label=option, variable=searchTypeVar, value=option)

# Sort dropdown menu
sortButton = Menubutton(entryFrame, text="Sort By", bg=RED_COLOR, relief="raised")
sortButton.grid(row=0, column=3, padx=5)
sortMenu = Menu(sortButton, tearoff=False)
sortButton.config(menu=sortMenu)
for option in sortOptions:  # Add dropdown menu options
    sortMenu.add_radiobutton(label=option, variable=sortVar, value=option)

# Flip sort button
flipOrderButton = Button(entryFrame, text="Flip Sort", bg=RED_COLOR, relief="raised", command=flipSort)
flipOrderButton.grid(row=0, column=4, padx=4)

# ============== List Box To Display Tasks ==============

myFrame = Frame(root)
myFrame.pack(pady=20)
TaskPanelViewFont = Font(family="Courier", size=15, weight="bold")
tasksPanelView = Listbox(myFrame, font=TaskPanelViewFont, width=53, height=11,
                         bg=BLUE_COLOR, bd=0, fg="#5c4033", highlightthickness=0,
                         selectbackground=BLUE_COLOR, selectforeground=WHITE_COLOR,
                         activestyle="none")
tasksPanelView.pack(side=LEFT, fill=BOTH)

tasksPanelViewScrollbar = Scrollbar(myFrame)
tasksPanelViewScrollbar.pack(side=RIGHT, fill=BOTH)
tasksPanelView.config(yscrollcommand=tasksPanelViewScrollbar.set)
tasksPanelViewScrollbar.config(command=tasksPanelView.yview)

# ============== Bottom Application Buttons ==============

buttonFrame = Frame(root, bg=WHITE_COLOR)
buttonFrame.pack(pady=20)

addNewTaskButton = Button(buttonFrame, text="Add Task", bg=LIGHT_GREEN_COLOR, width=12,
                          command=addNewTask)
addNewTaskButton.grid(row=0, column=0, padx=25, pady=5)

deleteTaskButton = Button(buttonFrame, text="Delete Task", bg=RED_COLOR, width=12,
                          command=deleteTask,)
deleteTaskButton.grid(row=1, column=0, padx=25, pady=5)

markDoneOrUndoneButton = Button(buttonFrame, text="Mark Done", bg=LIGHT_GREEN_COLOR, width=12,
                                command=markTaskDoneOrUndone)
markDoneOrUndoneButton.grid(row=0, column=1, padx=25, pady=5)

viewProgressButton = Button(buttonFrame, text="View Progress", bg=RED_COLOR, width=12,
                            command=viewProgress)
viewProgressButton.grid(row=1, column=2, padx=25, pady=5)

setReminderButton = Button(buttonFrame, text="Set Reminder", bg=LIGHT_GREEN_COLOR, width=12,
                           command=setTaskReminder)
setReminderButton.grid(row=0, column=2, padx=25, pady=5)

prioritizeOrUnprioritizeButton = Button(buttonFrame, text="Prioritize", bg=LIGHT_GREEN_COLOR, width=12,
                                        command=prioritizeOrUnprioritizeTask)
prioritizeOrUnprioritizeButton.grid(row=1, column=1, padx=25, pady=5)

# ============== More File Options Command Menu ==============

commandMenu = tk.Menu(root)
optionsMenu = tk.Menu(commandMenu, tearoff=False)
optionsMenu.add_command(label="Save", command=saveTaskList)
optionsMenu.add_command(label="Load", command=openTaskList)
optionsMenu.add_command(label="Clear All", command=clearAll)
commandMenu.add_cascade(label="File Options", menu=optionsMenu)
root.config(menu=commandMenu)

# ============== Track Application Clicks & Entries ==============

root.protocol("WM_DELETE_WINDOW", onClosing)

entryVar.trace("w", searchTasks)
sortVar.trace("w", sortOptionChanged)

root.bind("<Button-1>", onWindowClick)
entry.bind("<FocusIn>", searchBarFocusIn)
entry.bind("<FocusOut>", searchBarFocusOut)
tasksPanelView.bind('<<ListboxSelect>>', taskSelected)
tasksPanelView.bind("<FocusOut>", deselectTasks)
tasksPanelView.bind("<Double-Button-1>", showAndEditInfo)

# ============== Retrieve Prior App Status & Start Program ==============

loadSavedFile()
root.mainloop()
