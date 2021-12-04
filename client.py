# client.py
import socket
import sys
import traceback
from time import sleep

from gui import App, GuiThread

data = []


def start_client():

    try:
        gui = GuiThread()
        gui.start()
    except:
        print("Terrible error!")
        traceback.print_exc()

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect(('127.0.0.1', 12345))

    clients_input = input('What you want to proceed my dear client?\n')
    soc.send(clients_input.encode('utf8'))  # we must encode the string to bytes
    result_bytes = soc.recv(4096)  # the number means how the response can be in bytes
    result_string = result_bytes.decode('utf8')  # the return will be in bytes, so decode

    print('Result from server is {}'.format(result_string))
    gui.output_data(result_string)


if __name__ == '__main__':
    start_client()
