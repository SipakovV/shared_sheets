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


def get_query(thread):
    return thread.get_query()


def send_query(query, soc):
    packed_query = pickle.dumps(query)
    soc.send(packed_query)


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

    while True:
        query = get_query(gui)
        if query:
            print('query = ', query)
            send_query(query, soc)
        sleep(0.05)


    clients_input = input('What you want to proceed my dear client?\n')
    soc.send(clients_input.encode('utf8'))  # we must encode the string to bytes
    #result_bytes = soc.recv(4096)  # the number means how the response can be in bytes
    #result_string = result_bytes.decode('utf8')  # the return will be in bytes, so decode
    result_bytes = soc.recv(4096)  # the number means how the response can be in bytes
    #print(result_bytes, type(result_bytes))

    result_data = pickle.loads(result_bytes)
    #print('Result from server is {}'.format(result_data))
    gui.output_data(result_data)


if __name__ == '__main__':
    start_client()
