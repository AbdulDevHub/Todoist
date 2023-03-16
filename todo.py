import tkinter as tk
from tkinter import *
from tkinter.font import Font
import datetime

# Initialize the root and title as well as geometry
root = Tk()
root.title("To-Do List")
root.geometry("500x500")

# Create a font for the items in the list
font = Font(family="Comic Sans MS", size=30, weight="bold")

# Create a frame and a Listbox for the actual to do list and pack them accordingly
frame = tk.Frame(root)
frame.pack(pady=10)
to_do_list = tk.Listbox(frame, font=font, bd=0, bg="SystemButtonFace", width=25, height=8, fg="#464646",
                        highlightthickness=0, selectbackground="#a6a6a6", activestyle="none")
to_do_list.pack(side=LEFT, fill=BOTH)

# Create and add a scrollbar
scrollBar = tk.Scrollbar(frame)
scrollBar.pack(side=RIGHT, fill=BOTH)
to_do_list.config(yscrollcommand=scrollBar.set)
scrollBar.config(command=to_do_list.yview)

# Create an entry box for the input
entryBox = tk.Entry(root, width=50)
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
    if num < 10:
        entry = "0" + str(num) + "- " + item + "     " + date_string
    else:
        entry = str(num) + "- " + item + "     " + date_string
    if item:
        to_do_list.insert(tk.END, entry)
    num += 1


def remove_item():
    selection = to_do_list.curselection()
    if selection:
        index = selection[0]
        to_do_list.delete(index)

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

# Configure the layout of the buttons
add_button.grid(row=0, column=0)
delete_button.grid(row=0, column=1)
check_button.grid(row=0, column=2)


# main loop of the program
root.mainloop()