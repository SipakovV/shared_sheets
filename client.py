# client.py
import socket
import sys
import traceback
from time import sleep
import pickle

from gui import App, GuiThread

data = []


def start_client():

    try:
        gui = GuiThread()
        gui.setDaemon(True)
        gui.start()
    except:
        print("Terrible error!")
        traceback.print_exc()

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect(('127.0.0.1', 12345))

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
