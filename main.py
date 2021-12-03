import threading
import socket
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

    parent()
    '''
    myapp = App()
    
    #
    # here are method calls to the window manager class
    #
    myapp.master.title('1st window')
    myapp.master.maxsize(1000, 400)

    # start the program
    myapp.mainloop()

    myapp1 = App()

    #
    # here are method calls to the window manager class
    #
    myapp1.master.title('2nd window')
    myapp1.master.maxsize(1000, 400)

    # start the program
    myapp1.mainloop()
    '''

    filename = 'data.csv'
    data = []

    stop_thread = False

    sock = socket.socket()

    sock.bind(('', 9999))
    sock.listen(1)
    conn, addr = sock.accept()
    print('connected:', addr)

    with open(filename, newline='') as f:
        reader = csv.reader(f)
        try:
            for row in reader:
                #print(row)
                data.append(row)
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))

    #print(data)

    while True:
        data = conn.recv(1024)
        if not data:
            break
    conn.close()


if __name__ == '__main__':
    main()
