import threading
from time import sleep
import csv
import sys
import tkinter as tk

from gui import App

'''
class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        self.entrythingy = tk.Entry()
        self.entrythingy.pack()

        # Create the application variable.
        self.contents = tk.StringVar()
        # Set it to some value.
        self.contents.set("this is a variable")
        # Tell the entry widget to watch this variable.
        self.entrythingy["textvariable"] = self.contents

        # Define a callback for when the user hits return.
        # It prints the current value of the variable.
        self.entrythingy.bind('<Key-Return>',
                             self.print_contents)

    def print_contents(self, event):
        print("Hi. The current entry content is:",
              self.contents.get())
'''

root = tk.Tk()
myapp = App(root)
myapp.mainloop()

filename = 'data.csv'
data = []

stop_thread = False

with open(filename, newline='') as f:
    reader = csv.reader(f)
    try:
        for row in reader:
            #print(row)
            data.append(row)
    except csv.Error as e:
        sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))

print(data)

