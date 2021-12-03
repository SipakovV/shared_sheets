import threading
from time import sleep
import csv
import sys
import tkinter as tk

from gui import App


def main():

    myapp = App()
    
    #
    # here are method calls to the window manager class
    #
    myapp.master.title('1st window')
    myapp.master.maxsize(1000, 400)

    # start the program
    myapp.mainloop()

    data = []
    print(data)


if __name__ == '__main__':
    main()
