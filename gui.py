import tkinter as tk
from threading import Thread
from time import sleep
from queue import Queue
#test.txt srelgiuhsr


class App(tk.Frame):
    data = None  # эту переменную выводите на экран
    max_pages = 1
    page = 1
    queue = Queue()
    x = 1
    y = 2
    cell_value = 5

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
        self.entrythingy.bind('<Key-F5>', self.get_page_query)
        self.entrythingy.bind('<Key-F4>', self.get_prev_page)
        self.entrythingy.bind('<Key-F6>', self.get_next_page)
        self.entrythingy.bind('<Key-F1>', self.edit_query)
        self.entrythingy.bind('<Key-F2>', self.confirm_edit)
        self.entrythingy.bind('<Key-F3>', self.rollback_edit)
        self.entrythingy.bind('<Key-Return>', self.print_contents)

    def print_contents(self, event):
        print('Hi. The current entry content is:', self.contents.get())

    def send_to_master(self, query):
        self.queue.put(query)
        print('send_to_master:', query)

    def get_page_query(self, event):
        self.send_to_master(['get', self.page])

    def get_next_page(self, event):
        self.page += 1
        self.get_page_query(event)

    def get_prev_page(self, event):
        self.page -= 1
        self.get_page_query(event)

    def edit_query(self, event):
        self.send_to_master(['edit', self.page, self.x, self.y])

    def confirm_edit(self, event):
        self.send_to_master(['confirm', self.cell_value])

    def rollback_edit(self, event):
        self.send_to_master(['rollback'])

    def set_data(self, data):
        self.data = data
        #print('gui_data = ', self.data)
        self.draw_page(self.data)

    def draw_page(self, data):
        print('GUI got data ', data)


class GuiThread(Thread):

    #def __init__(self):
    #    Thread.__init__(self)

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

    def get_query(self):
        if self.app.queue.empty():
            return None
        else:
            return self.app.queue.get(self)

    def set_data(self, data):
        self.app.set_data(data)

    def set_number_of_pages(self, num):
        self.app.max_pages = num
        print(f'Pages: {self.app.max_pages}')
