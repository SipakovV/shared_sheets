import tkinter as tk
from threading import Thread
from time import sleep
#test.txt srelgiuhsr

class App(tk.Frame):
    data = None  # эту переменную выводите на экран

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()

        self.entrythingy = tk.Entry()
        self.entrythingy.pack()

        # Create the application variable.
        self.contents = tk.StringVar()
        # Set it to some value.
        self.contents.set('this is a variable')
        
        #Ввожу кнопки, пока они нефункциональны (Aksolot), чтобы привязать их к функциям на определённые действия, используйте аргумент command функции tk.Button
        self.btn = tk.Button(master, text = "Forward", activebackground='#eeeeee',activeforeground='#000000',bg='#a0a000',fg='#ffffff',width=10)
        self.btn.place(x=10, y=50)
        self.bt2 = tk.Button(master, text = "Backward", activebackground='#eeeeee',activeforeground='#000000',bg='#a0a000',fg='#ffffff',width=10)
        self.bt2.place(x=160, y=50)
        self.bt3 = tk.Button(master, text = "Refresh", activebackground='#eeeeee',activeforeground='#000000',bg='#00a000',fg='#ffffff',width=10)
        self.bt3.place(x=310, y=50)
        self.bt4 = tk.Button(master, text = "Quit", activebackground='#eeeeee',activeforeground='#000000',bg='#a00000',fg='#ffffff',width=10)
        self.bt4.place(x=460, y=50)
        
        
        # Tell the entry widget to watch this variable.
        self.entrythingy['textvariable'] = self.contents

        # Define a callback for when the user hits return.
        # It prints the current value of the variable.
        self.entrythingy.bind('<Key-Return>', self.print_contents)

    def print_contents(self, event):
        print('Hi. The current entry content is:', self.contents.get())

    def set_data(self, data):
        self.data = data
        print('gui_data = ', data)


class GuiThread(Thread):

    def run(self):
        print('GUI thread started!')
        self.app = App()
        self.app.master.title('Window')
        self.app.master.maxsize(1000, 400)
        self.app.mainloop()
        print('GUI thread ended!')

    def output_data(self, data):
        self.app.set_data(data)
        #print(f'{data=}')


