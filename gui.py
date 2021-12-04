import tkinter as tk
from threading import Thread
from time import sleep


class App(tk.Frame):

    data = None

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()

        self.entrythingy = tk.Entry()
        self.entrythingy.pack()

        # Create the application variable.
        self.contents = tk.StringVar()
        # Set it to some value.
        self.contents.set('this is a variable')
        # Tell the entry widget to watch this variable.
        self.entrythingy['textvariable'] = self.contents

        # Define a callback for when the user hits return.
        # It prints the current value of the variable.
        self.entrythingy.bind('<Key-Return>', self.print_contents)

    def print_contents(self, event):
        print('Hi. The current entry content is:',
              self.contents.get())

    def get_data(self, data):
        self.data = data

class GuiThread(Thread):

    def run(self):
        print('GUI thread started!')
        app = App()
        app.master.title('Window')
        app.master.maxsize(1000, 400)
        app.mainloop()
        print('GUI thread ended!')

