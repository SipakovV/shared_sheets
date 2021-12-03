import threading
from time import sleep
import csv
import sys
import tkinter as tk

from gui import App


def child(tid):
    myapp = App()

    #
    # here are method calls to the window manager class
    #
    myapp.master.title(str(tid)+' window')
    myapp.master.maxsize(1000, 400)

    # start the program
    myapp.mainloop()
    print('Hello from thread %d' % tid)


def parent():
    for i in range(2):
        # создание дочернего потока
        t = threading.Thread(target=child, args=(i+1,))
        t.start()  # запуск дочернего потока
        sleep(5)
    print('Parent thread finished')


def main():

    #parent()

    '''
    myapp = App()
    
    #
    # here are method calls to the window manager class
    #
    myapp.master.title('1st window')
    myapp.master.maxsize(1000, 400)

    # start the program
    myapp.mainloop()
    '''

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

    #print(data)


if __name__ == '__main__':
    main()
