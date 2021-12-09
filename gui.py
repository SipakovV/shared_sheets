import tkinter as tk
from tkinter import *
from threading import Thread
from time import sleep, perf_counter
from queue import Queue
import sys
#test.txt srelgiuhsr


class App(tk.Frame):

    data = [["???" for y in range(10)] for x in range(10)]  #None # эту переменную выводите на экран
    busy_cells = []

    max_pages = 1
    page = 1
    row_size = 10
    page_size = 10
    cell_value = 5
    edited_cell = (99, 99)

    queue = Queue()

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.message = StringVar()
        self.entrythingy = tk.Entry()
        #self.entrythingy.pack()

        # Create the application variable.
        #self.contents = tk.StringVar()
        # Set it to some value.
        #self.contents.set('this is a variable')
        
        #заголовки
        header = ["Series_reference", "Period", "Data_value", "Suppressed", "STATUS", "UNITS", "Magnitude", "Subject", "Group", "Series_title_1"]
        i = 0

        while i < self.row_size:
            hdr = tk.Label(text=header[i])
            hdr.place(x=70+(150*i),y=20)
            i+=1
        
        #нумерация строк
        self.row_number = [tk.StringVar() for j in range(self.page_size)]
        self.row_label = [None for j in range(self.page_size)]
        i = 0
        while i < self.page_size:
            self.row_label[i] = tk.Label(textvariable=self.row_number[i])
            self.row_label[i].place(x=0,y=63+(50*i))
            i+=1
        
        # кнопки управления страницами
        self.bt2 = tk.Button(master, text="Previous page", activebackground='#eeeeee', activeforeground='#000000',
                             bg='#a0a000', fg='#ffffff', width=13, command=self.get_prev_page)
        self.bt2.place(x=70, y=550, width=150, height=50)
        self.bt3 = tk.Button(master, text="Refresh", activebackground='#eeeeee', activeforeground='#000000',
                             bg='#00a000', fg='#ffffff', width=13, command=self.get_page_query)
        self.bt3.place(x=220, y=550, width=150, height=50)
        self.btn = tk.Button(master, text="Next page", activebackground='#eeeeee', activeforeground='#000000',
                             bg='#a0a000', fg='#ffffff', width=13, command=self.get_next_page)
        self.btn.place(x=370, y=550, width=150, height=50)

        self.btn = tk.Button(master, text=">>>", activebackground='#eeeeee', activeforeground='#000000',
                             bg='#a0a000', fg='#ffffff', width=13, command=self.confirm_edit)
        self.message_entry = Entry(self.master, textvariable=self.message, bg='#a0a000', fg='#ffffff')
        self.message_entry.place(x=820, y=550, width=150, height=50)
        self.btn.place(x=520, y=550, width=150, height=50)
        self.btn = tk.Button(master, text="Rollback", activebackground='#eeeeee', activeforeground='#000000',
                             bg='#a0a000', fg='#ffffff', width=13, command=self.rollback_edit)
        self.btn.place(x=670, y=550, width=150, height=50)


        '''
        # таблица (command=self.edit_query заменить лямбда-функцией)
        i = 0
        while i < self.page_size:
            j = 0
            while j < self.row_size:
                if j % 2 == 0:
                    self.tab = tk.Button(self.master, text=self.data[i][j], activebackground='#111111', activeforeground='#ffffff', bg='#bbbbff', fg='#000000', height=2, width=13, relief=tk.RIDGE, wraplength=140, command=self.edit_query)
                else:
                    self.tab = tk.Button(self.master, text=self.data[i][j], activebackground='#111111', activeforeground='#ffffff', bg='#bbffbb', fg='#000000', height=2, width=13, relief=tk.RIDGE, wraplength=140, command=self.edit_query)
                self.tab.place(x=10+(150*j), y=50+(50*i))
                j += 1
            i += 1
        '''
        self.draw_page()
        
        # Tell the entry widget to watch this variable.
        #self.entrythingy['textvariable'] = self.contents

        # Define a callback for when the user hits return.
        # It prints the current value of the variable.
        self.master.bind('<Key-F5>', self.get_page_query_bind)
        self.master.bind('<Key-F4>', self.get_prev_page_bind)
        self.master.bind('<Key-F6>', self.get_next_page_bind)
        #self.entrythingy.bind('<Key-F1>', self.edit_query)
        #self.entrythingy.bind('<Key-F2>', self.confirm_edit)
        #self.entrythingy.bind('<Key-F3>', self.rollback_edit)
        #self.entrythingy.bind('<Key-Return>', self.print_contents)

    def vvod_buttom(self):
        i = 0
        while i < self.page_size:
            j = 0
            while j < self.row_size:
                self.data[i][j] = self.mass[i][j].get()
                j += 1
            i += 1

    def test(self, i, j, *args): #просто для теста
        if self.Flag:
            if ((self.pred[0] != i) or (self.pred[1] != j)):
                '''
                print("нажата ячейка " + str(i) + " " + str(j))
                print("тут")
                тут должна быть проверка доступности ячейки
                '''
                self.edit_query(i, j)

                self.pred[0] = i
                self.pred[1] = j

    def print_contents(self, event):
        print('The current entry content is:', self.contents.get())

    def send_to_master(self, query: object) -> object:
        self.queue.put(query)
        print('send_to_master:', query)

    def get_page_query_bind(self, event):
        self.get_page_query()

    def get_next_page_bind(self, event):
        self.get_next_page()

    def get_prev_page_bind(self, event):
        self.get_prev_page()

    def get_page_query(self):
        self.send_to_master(['get', self.page])

    def get_next_page(self):
        self.page += 1
        self.get_page_query()

    def get_prev_page(self):
        self.page -= 1
        self.get_page_query()

    def edit_query(self, row: object, col: object) -> object:
        self.rollback_edit()
        self.edited_cell = row, col
        print(f'Time before sending: {perf_counter()}')
        self.send_to_master(['edit', self.page, row, col])

    def confirm_edit(self):
        self.cell_value = self.message.get()
        self.edited_cell = (99, 99)
        self.send_to_master(['confirm', self.cell_value])
        #self.draw_page()
        self.refresh()

    def rollback_edit(self):
        self.send_to_master(['rollback'])

    def set_data(self, data):
        self.data = data
        #print('gui_data = ', self.data)
        #self.draw_page()
        self.refresh()

    def draw_page(self):
        start_time = perf_counter()
        print(f'Time before drawing: {start_time}')
        self.pred = [99,99]
        self.Flag = 0
        print('GUI got data ')
        #print('GUI got data ', data)
        self.mass = [[tk.StringVar() for j in range(self.row_size)] for i in range(self.page_size)]
        self.tab = [[0 for j in range(self.row_size)] for i in range(self.page_size)]
        self.vrbl = [[tk.StringVar() for j in range(self.row_size)] for i in range(self.page_size)]
        # таблица в функции (command=self.edit_query заменить лямбда-функцией)
        i = 0
        while i < self.page_size:
            j = 0
            while j < self.row_size:
                self.mass[i][j].trace("w", lambda name1, name2, op, x=i, y=j: self.test(x,y,name1,name2,op))
                j += 1
            i += 1

        i = 0
        while i < self.page_size:
            j = 0
            while j < self.row_size:
                if j % 2 == 0:
                    cell_bg_color = '#f0f0f0'
                    cell_active_bg_color = '#f5f5f5'
                    cell_fg_color = '#000000'
                else:
                    cell_bg_color = '#f9f9f9'
                    cell_active_bg_color = '#ffffff'
                    cell_fg_color = '#000000'

                coords = (i, j)
                
                if coords != self.edited_cell:
                    print(self.data[i][j])
                    #self.vrbl[i][j] = tk.StringVar(self.data[i][j])
                    self.tab[i][j] = tk.Button(self.master, textvariable=self.vrbl[i][j], activebackground=cell_active_bg_color, activeforeground='#000000',
                             bg=cell_bg_color, fg=cell_fg_color, width=10, command=(lambda x=i, y=j: self.edit_query(x, y)))
                else:
                    self.tab[i][j] = tk.Entry(self.master, textvariable=self.mass[i][j], bg=cell_bg_color, fg=cell_fg_color)
                    self.tab[i][j].bind('<Key-Return>', self.confirm_edit)
                    self.tab[i][j].insert(0, self.data[i][j])
                self.tab[i][j].place(x=70+(150*j), y=50+(50*i), width=150, height=50)
                j += 1
            i += 1
        self.Flag = 1
        end_time = perf_counter()
        execution_time = end_time - start_time
        print(f'Drawing time: {execution_time}')

    def refresh(self):
        i = 0
        while i < self.page_size:
            j = 0
            while j < self.page_size:
                #self.data[i][j].set(self.mass[i][j])
                #self.tab[i][j].set(text=self.mass[i][j])
                self.vrbl[i][j].set(self.data[i][j])
                j+=1
            self.row_number[i].set((self.page-1)*self.page_size+i+1)
            i+=1
    
    def set_header(self, header):
        self.header = header

    def set_busy_cells(self, busy_cells):
        self.busy_cells = busy_cells

    def set_row_size(self, row_size):
        self.row_size = row_size

    def set_modified_cell(self, coords):
        self.data[coords[0]][coords[1]] = coords[2]
        self.refresh()
        #self.update_cell(coords)


class GuiThread(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print('GUI thread started!')
        self.app = App()
        self.app.master.title('Window')
        self.app.master.minsize(1600, 620)
        self.app.master.maxsize(1600, 620)
        self.app.mainloop()
        print('GUI thread ended!')

    def output_data(self, data):
        if data['type'] == 'full':
            self.app.set_header(data['header'])
            self.app.set_busy_cells(data['edit'])
            self.app.master.title(data['filename'])
            self.app.set_row_size(data['row_size'])
            self.app.set_data(data['table'])
        elif data['type'] == 'part':
            self.app.set_busy_cells(data['edit'])
            if data['modified']:
                self.app.set_modified_cell(data['modified'])

        #print(f'{data=}')

    def get_query(self):
        if self.app.queue.empty():
            return None
        else:
            return self.app.queue.get(self)

    def set_number_of_pages(self, num):
        self.app.max_pages = num
        print(f'Pages: {self.app.max_pages}')
