# server.py
import socket
import sys
from threading import Thread
import traceback
import tkinter as tk
from time import sleep
import csv
import pickle

from gui import App


FILENAME = 'data.csv'
PAGE_SIZE = 10


busy_cells = {}

data = []
number_of_pages = 0


def read_csv():
    with open(FILENAME, newline='') as f:
        reader = csv.reader(f)
        try:
            i = 40
            for row in reader:
                data.append(row)
                i -= 1
                if i < 0:
                    break
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(FILENAME, reader.line_num, e))
    return data


def process_query(conn, query):
    print("Processing query...")

    query_dict = {
        #'get': send_page(conn, query[1]),
        #'edit': busy_cells['']
    }

    print(conn, type(conn))
    #query_dict[query[0]]


def send_page(conn, page):
    rows_from = (page - 1) * PAGE_SIZE + 1
    rows_to = page * PAGE_SIZE + 1
    table = data[rows_from:rows_to]
    #print(table)

    packed_table = pickle.dumps(table)
    conn.sendall(packed_table)


def client_thread(conn, ip, port, MAX_BUFFER_SIZE = 4096):

    global number_of_pages
    pages_num = pickle.dumps([number_of_pages])
    conn.sendall(pages_num)

    while True:
        # the input is in bytes, so decode it
        input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)

        print('Test')
        # MAX_BUFFER_SIZE is how big the message can be
        # this is test.txt if it's sufficiently big

        siz = sys.getsizeof(input_from_client_bytes)
        if siz >= MAX_BUFFER_SIZE:
            print("The length of input is probably too long: {}".format(siz))

        # decode input and strip the end of line

        input_from_client1 = pickle.loads(input_from_client_bytes)
        print('Query = ', input_from_client1)

        process_query(conn, input_from_client1)

    #conn.close()  # close connection
    #print('Connection ' + ip + ':' + port + " ended")


def start_server():
    global data
    global number_of_pages
    data = read_csv()
    number_of_pages = len(data) // PAGE_SIZE + 1

    print('Csv file read (pages:', number_of_pages, ')')

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this is for easy starting/killing the app
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Socket created')

    try:
        soc.bind(("127.0.0.1", 12345))
        print('Socket bind complete')
    except socket.error as msg:
        print('Bind failed. Error : ' + str(sys.exc_info()))
        sys.exit()

    # Start listening on socket
    soc.listen(5)
    print('Socket now listening')

    # for handling task in separate jobs we need threading

    # this will make an infinite loop needed for
    # not resetting server for every client
    while True:
        conn, addr = soc.accept()
        ip, port = str(addr[0]), str(addr[1])
        print('Accepting connection from ' + ip + ':' + port)
        try:
            Thread(target=client_thread, args=(conn, ip, port), daemon=True).start()
        except:
            print("Terrible error!")
            traceback.print_exc()
    soc.close()


if __name__ == '__main__':
    start_server()
