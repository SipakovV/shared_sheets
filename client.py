# client.py
import socket
import sys
import traceback
from time import sleep
import pickle
from queue import Queue
import pickle

from gui import App, GuiThread

data = []

queue_to_gui = Queue()
queue_from_gui = Queue()


def get_query(gui):
    return gui.get_query()


def send_query(query, soc):
    packed_query = pickle.dumps(query)
    soc.send(packed_query)


def get_data_from_server(soc, gui):
    result_bytes = soc.recv(4096)  # the number means how the response can be in bytes
    result_data = pickle.loads(result_bytes)
    gui.output_data(result_data)


def get_number_of_pages(soc, gui):
    pages_num_bytes = soc.recv(40)
    pages_num = pickle.loads(pages_num_bytes)[0]
    gui.set_number_of_pages(pages_num)


def start_client():

    try:
        gui = GuiThread()

        gui.setDaemon(True)
        gui.start()
    except:
        print("Terrible error!")
        traceback.print_exc()

    sleep(1)

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect(('127.0.0.1', 12345))

    get_number_of_pages(soc, gui)


    while True:
        query = get_query(gui)
        if query:
            print('query = ', query)
            send_query(query, soc)
            get_data_from_server(soc, gui)
        sleep(0.05)

    """
    clients_input = input('What you want to proceed my dear client?\n')
    soc.send(clients_input.encode('utf8'))  # we must encode the string to bytes
    result_bytes = soc.recv(4096)  # the number means how the response can be in bytes

    result_data = pickle.loads(result_bytes)
    gui.output_data(result_data)
    """


if __name__ == '__main__':
    start_client()
