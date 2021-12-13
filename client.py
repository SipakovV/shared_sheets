# client.py
import socket
import sys
import traceback
from threading import Thread
from time import sleep
import pickle
from queue import Queue
import pickle

from gui import App, GuiThread

data = []

queue_to_gui = Queue()
queue_from_gui = Queue()


def listening_thread(soc, gui, MAX_BUFFER_SIZE = 4096):
    while True:
        try:
            result_data = get_data_from_server(soc)
        except:
            print('Error while getting data from server')
            traceback.print_exc()
            break
        try:
            gui.output_data(result_data)
        except:
            print('Error while data output to gui')
            traceback.print_exc()
            break


def get_query(gui):
    return gui.get_query()


def send_query(query, soc):
    packed_query = pickle.dumps(query)
    soc.send(packed_query)


def send_status_query(soc):
    query = ['status']
    packed_query = pickle.dumps(query)
    soc.send(packed_query)


def get_data_from_server(soc):
    result_bytes = soc.recv(4096)  # the number means how the response can be in bytes
    result_data = pickle.loads(result_bytes)
    #print(result_data)
    return result_data


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
        print("Error while starting GUI thread")
        traceback.print_exc()

    sleep(1)

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect(('127.0.0.1', 12345))

    get_number_of_pages(soc, gui)

    try:
        Thread(target=listening_thread, args=(soc, gui), daemon=True).start()
    except:
        print("Error while starting listening thread")
        traceback.print_exc()

    while True:
        query = get_query(gui)
        if query:
            print('query = ', query)
            send_query(query, soc)

        sleep(0.1)
        send_status_query(soc)
        if not gui.is_alive():
            break

    """
    clients_input = input('What you want to proceed my dear client?\n')
    soc.send(clients_input.encode('utf8'))  # we must encode the string to bytes
    result_bytes = soc.recv(4096)  # the number means how the response can be in bytes

    result_data = pickle.loads(result_bytes)
    gui.output_data(result_data)
    """


if __name__ == '__main__':
    start_client()
