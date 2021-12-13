import tkinter as tk
from tkinter import *
from threading import Thread
from time import perf_counter
from queue import Queue

MAX_BUFFER_SIZE = 4096

class App(tk.Frame):

    data = [["???" for y in range(10)] for x in range(10)]
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

        # заголовки
        header = ["Series_reference", "Period", "Data_value", "Suppressed", "STATUS", "UNITS", "Magnitude", "Subject", "Group", "Series_title_1"]
        i = 0

        while i < self.row_size:
            hdr = tk.Label(text=header[i])
            hdr.place(x=70+(150*i),y=20)
            i += 1
        
        # нумерация строк
        self.row_number = [tk.StringVar() for j in range(self.page_size)]
        self.row_label = [None for j in range(self.page_size)]
        i = 0
        while i < self.page_size:
            self.row_label[i] = tk.Label(textvariable=self.row_number[i])
            self.row_label[i].place(x=0,y=63+(50*i))
            i += 1
        
        # кнопки управления страницами
        self.bt2 = tk.Button(master, text="Previous page", activebackground='#eeeeee', activeforeground='#000000',
                             bg='#a0a000', fg='#ffffff', width=13, command=self.get_prev_page)
        self.bt2.place(x=70, y=550, width=150, height=50)
        self.bt2.place_forget()
        self.bt3 = tk.Button(master, text="Refresh", activebackground='#eeeeee', activeforeground='#000000',
                             bg='#00a000', fg='#ffffff', width=13, command=self.get_page_query)
        self.bt3.place(x=220, y=550, width=150, height=50)
        self.btn = tk.Button(master, text="Next page", activebackground='#eeeeee', activeforeground='#000000',
                             bg='#a0a000', fg='#ffffff', width=13, command=self.get_next_page)
        self.btn.place(x=370, y=550, width=150, height=50)
        self.btn.place_forget()
        self.draw_page()
        self.get_page_query()
        self.refresh()
        self.master.bind('<Key-F5>', self.get_page_query_bind)
        self.master.bind('<Key-F4>', self.get_prev_page_bind)
        self.master.bind('<Key-F6>', self.get_next_page_bind)

    def vvod_buttom(self):
        i = 0
        while i < self.page_size:
            j = 0
            while j < self.row_size:
                self.data[i][j] = self.mass[i][j].get()
                j += 1
            i += 1

    def test(self, i, j):  # просто для теста
        if self.Flag:
            if ((self.pred[0] != i) or (self.pred[1] != j)):
                self.edit_query(i, j)
                self.pred[0] = i
                self.pred[1] = j

    def print_contents(self, event):
        print('The current entry content is:', self.contents.get())

    def send_to_master(self, query: object) -> object:
        self.queue.put(query)

    def get_page_query_bind(self, event):
        self.get_page_query()

    def get_next_page_bind(self, event):
        self.get_next_page()

    def get_prev_page_bind(self, event):
        self.get_prev_page()

    def get_page_query(self):
        self.rollback_edit()
        self.message_entry.place_forget()
        self.message_entry.delete(0, END)
        self.send_to_master(['get', self.page])

    def get_next_page(self):
        if self.page < self.max_pages-1:
            self.page += 1
            self.get_page_query()

    def get_prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.get_page_query()

    def edit_query(self, row: object, col: object) -> object:
        if (row, col) in self.busy_cells:
            return

        self.cell_color_reset(self.edited_cell[0], self.edited_cell[1])
        self.edited_cell = row, col
        y = int(50 + (50 * self.edited_cell[0]))
        x = int(70 + (150 * self.edited_cell[1]))
        print(x, y)

        print(self.edited_cell)

        self.message_entry.delete(0, END)
        self.message_entry.insert(0, self.vrbl[row][col].get())
        self.message_entry.place(x=x, y=y, width=150, height=50)
        self.rollback_edit()
        self.send_to_master(['edit', self.page, row, col])

    def confirm_edit(self):
        if len(self.message.get()) >= MAX_BUFFER_SIZE:
            print(f'Error: too many symbols in cell (max: {MAX_BUFFER_SIZE}')
            return
        self.cell_value = self.message.get()
        self.message_entry.place_forget()

        self.edited_cell = (99, 99)
        self.send_to_master(['confirm', self.cell_value])
        self.refresh()

    def confirm_edit_bind(self, event):
        self.confirm_edit()

    def rollback_edit(self):
        self.send_to_master(['rollback'])

    def rollback_edit_bind(self, event):
        self.message_entry.place_forget()
        self.rollback_edit()

    def set_data(self, data):
        self.data = data
        self.refresh()

    def draw_page(self):
        start_time = perf_counter()
        self.pred = [99,99]
        self.Flag = 0
        print('GUI got data ')
        self.mass = [[tk.StringVar() for j in range(self.row_size)] for i in range(self.page_size)]
        self.tab = [[0 for j in range(self.row_size)] for i in range(self.page_size)]
        self.vrbl = [[tk.StringVar() for j in range(self.row_size)] for i in range(self.page_size)]
        # таблица в функции (command=self.edit_query заменить лямбда-функцией)
        i = 0
        while i < self.page_size:
            j = 0
            while j < self.row_size:
                self.mass[i][j].trace("w", lambda name1, name2, op, x=i, y=j: self.test(x, y))
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
                    self.tab[i][j] = tk.Button(self.master, textvariable=self.vrbl[i][j], activebackground=cell_active_bg_color, activeforeground='#000000',
                             bg=cell_bg_color, fg=cell_fg_color, width=10, command=(lambda x=i, y=j: self.edit_query(x, y)))
                else:
                    self.tab[i][j] = tk.Entry(self.master, textvariable=self.mass[i][j], bg=cell_bg_color, fg=cell_fg_color)
                    self.tab[i][j].bind('<Key-Return>', self.confirm_edit)
                    self.tab[i][j].insert(0, self.data[i][j])
                self.tab[i][j].place(x=70+(150*j), y=50+(50*i), width=150, height=50)
                self.message_entry = Entry(self.master, textvariable=self.message, bg='#a0a000', fg='#ffffff')
                self.message_entry.config(bg='#ffffff', fg='#000000')
                self.message_entry.bind('<Key-Return>', self.confirm_edit_bind)
                self.message_entry.bind('<Key-Escape>', self.rollback_edit_bind)
                self.message_entry.place(x=820, y=550, width=150, height=50)
                self.message_entry.place_forget()
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
                self.vrbl[i][j].set(self.data[i][j])
                self.cell_color(i, j)
                j += 1
            self.row_number[i].set((self.page-1)*self.page_size+i+1)
            i += 1
        self.btn.place(x=370, y=550, width=150, height=50)
        self.bt2.place(x=70, y=550, width=150, height=50)
        if self.page == self.max_pages-1:
            self.btn.place_forget()
        if self.page == 1:
            self.bt2.place_forget()
    
    def set_header(self, header):
        self.header = header

    def set_busy_cells(self, busy_cells):
        if self.busy_cells != busy_cells:
            for cell in self.busy_cells:
                self.cell_color_reset(cell[0], cell[1])
            self.busy_cells = busy_cells
            print('busy: ', self.busy_cells)
            for cell in self.busy_cells:
                self.cell_color(cell[0], cell[1])

    def set_row_size(self, row_size):
        self.row_size = row_size

    def set_modified_cell(self, coords):
        self.data[coords[0]][coords[1]] = coords[2]
        self.refresh()

    def cell_color(self, i, j):
        if i >= self.page_size or j >= self.row_size:
            return
        if (i, j) in self.busy_cells:
            self.tab[i][j].config(bg="#d5d522", activebackground="#dddd33")

        else:
            if j % 2 == 0:
                cell_bg_color = '#f0f0f0'
                cell_active_bg_color = '#f5f5f5'
            else:
                cell_bg_color = '#f9f9f9'
                cell_active_bg_color = '#ffffff'
            self.tab[i][j].config(bg=cell_bg_color, activebackground=cell_active_bg_color)

    def cell_color_reset(self, i, j):
        if i >= self.page_size or j >= self.row_size:
            return
        if j % 2 == 0:
            cell_bg_color = '#f0f0f0'
            cell_active_bg_color = '#f5f5f5'
        else:
            cell_bg_color = '#f9f9f9'
            cell_active_bg_color = '#ffffff'
        self.tab[i][j].config(bg=cell_bg_color, activebackground=cell_active_bg_color)


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

    def get_query(self):
        if self.app.queue.empty():
            return None
        else:
            return self.app.queue.get(self)

    def set_number_of_pages(self, num):
        self.app.max_pages = num
        print(f'Pages: {self.app.max_pages}')
