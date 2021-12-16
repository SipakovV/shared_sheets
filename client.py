# client.py
import socket
import traceback
from threading import Thread
from time import sleep
from queue import Queue
import pickle

from gui import App, GuiThread

SERVER_ADDRESS = ("127.0.0.1", 12345)

MAX_BUFFER_SIZE = 4096
data = []

queue_to_gui = Queue()
queue_from_gui = Queue()


def listening_thread(soc, gui):  # поток, обрабатывающий пакеты с сервера
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


def get_query(gui):  # получение запроса от интерфейса
    return gui.get_query()


def send_query(query, soc):  # отправка запроса серверу
    packed_query = pickle.dumps(query)
    soc.send(packed_query)


def send_status_query(soc):  # отправка запроса статуса серверу
    query = ['status']
    packed_query = pickle.dumps(query)
    soc.send(packed_query)


def get_data_from_server(soc):  # принятие пакета от сервера
    result_bytes = soc.recv(MAX_BUFFER_SIZE)
    result_data = pickle.loads(result_bytes)
    return result_data


def get_number_of_pages(soc, gui):  # принятие количества страниц
    pages_num_bytes = soc.recv(40)
    pages_num = pickle.loads(pages_num_bytes)[0]
    gui.set_number_of_pages(pages_num)


def start_client():  # запуск программы
    try:
        gui = GuiThread()
        gui.setDaemon(True)
        gui.start()
    except:
        print("Error while starting GUI thread")
        traceback.print_exc()

    sleep(1)

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect(SERVER_ADDRESS)

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


if __name__ == '__main__':
    start_client()
