import tkinter as tk
from tkinter import *
from tkinter.font import Font
import datetime


# Initialize the root and title as well as geometry
root = Tk()
root.title("To-Do List")
root.geometry("500x500")

# Create a font for the items in the list
font = Font(family="Comic Sans MS", size=20, weight="bold")

# Create a frame for the search box and search button
search_frame = Frame(root)
search_frame.pack(pady=5)

# Create an entry box for the search
search_box = tk.Entry(search_frame, width=35)
search_box.insert(0, "Search for a task using keywords")


# Create commands for the search box
def on_entry_click(event):
    if search_box.get() == "Search for a task using keywords":
        search_box.delete(0, tk.END)
        search_box.insert(0, '')


def on_focusout(event):
    if search_box.get() == '':
        search_box.insert(0, "Search for a task using keywords")


search_box.bind('<FocusIn>', on_entry_click)
search_box.bind('<FocusOut>', on_focusout)
search_box.pack(side=LEFT)


# Create a frame and a Listbox for the actual to do list and pack them accordingly
frame = tk.Frame(root)
frame.pack(pady=10)
to_do_list = tk.Listbox(frame, font=font, bd=0, bg="SystemButtonFace", width=35, height=12, fg="#464646",
                        highlightthickness=0, selectbackground="#a6a6a6", activestyle="none")
to_do_list.pack(side=LEFT, fill=BOTH)


# Create and add a scrollbar
scrollBar = tk.Scrollbar(frame)
scrollBar.pack(side=RIGHT, fill=BOTH)
to_do_list.config(yscrollcommand=scrollBar.set)
scrollBar.config(command=to_do_list.yview)


# Create an entry box for the input
entryBox = tk.Entry(root, width=50)
entryBox.insert(0, "Insert task, be sure to keep it under 30 characters")


# Create commands for the entry box
def on_entry_click(event):
    if entryBox.get() == "Insert task, be sure to keep it under 30 characters":
        entryBox.delete(0, tk.END)
        entryBox.insert(0, '')


def on_focusout(event):
    if entryBox.get() == '':
        entryBox.insert(0, "Insert task, be sure to keep it under 30 characters")


entryBox.bind('<FocusIn>', on_entry_click)
entryBox.bind('<FocusOut>', on_focusout)
entryBox.pack(pady=5)


# Create another frame for all the buttons
buttonFrame = tk.Frame(root)
buttonFrame.pack(pady=10)

# Create a variable for the numbering of items in the list
num = 1


# functions for item commands in the to do list
def add_item():
    global num
    curr_date = datetime.datetime.now()
    date_string = curr_date.strftime("%d-%m")
    item = entryBox.get()
    num_spaces = " " * (30 - len(item))
    if num < 10:
        entry = "0" + str(num) + "- " + item + num_spaces + date_string
    else:
        entry = str(num) + "- " + item + num_spaces + date_string
    if item:
        to_do_list.insert(tk.END, entry)
        original_items.append(entry)
    num += 1


def prioritize_item():
    selection = to_do_list.curselection()
    if selection:
        index = selection[0]
        to_do_list.itemconfig(index, {'bg': 'red'})
        to_do_list.selection_clear(0, END)


def remove_item():
    selection = to_do_list.curselection()
    if selection:
        index = selection[0]
        item = to_do_list.get(index)
        to_do_list.delete(index)
        original_items.remove(item)

    new_num = 1
    for i in range(to_do_list.size()):
        entry = to_do_list.get(i)
        if new_num < 10:
            entry = "0" + str(new_num) + "- " + entry[4:]
        else:
            entry = str(new_num) + "- " + entry[4:]
        to_do_list.delete(i)
        to_do_list.insert(i, entry)
        new_num += 1


# Make the buttons for the button frame
add_button = tk.Button(buttonFrame, text="Add Item", command=add_item)
delete_button = tk.Button(buttonFrame, text="Delete Item", command=remove_item)
check_button = tk.Button(buttonFrame, text="Check Item Off")
prioritize_button = tk.Button(buttonFrame, text="Prioritize", command=prioritize_item)

# Configure the layout of the buttons
add_button.grid(row=0, column=0)
delete_button.grid(row=0, column=1)
check_button.grid(row=0, column=2)
prioritize_button.grid(row=0, column=3)

# Keep a copy of all items in the to do list
original_items = []
for i in range(to_do_list.size()):
    original_items.append(to_do_list.get(i))


# Create a function for the search button
def search_item():
    search_text = search_box.get()
    if search_text:
        to_do_list.delete(0, tk.END)
        for item in original_items:
            if search_text.lower() in item.lower():
                to_do_list.insert(tk.END, item)


def restore_item():
    to_do_list.delete(0, tk.END)
    for item in original_items:
        to_do_list.insert(tk.END, item)


# Create a restore button for the list
restore_button = tk.Button(search_frame, text="Restore", command=restore_item)
restore_button.pack(side=RIGHT)

# Creating the search button for the search bar
search_button = tk.Button(search_frame, text="Search", command=search_item)
search_button.pack(side=LEFT)


# main loop of the program
root.mainloop()
