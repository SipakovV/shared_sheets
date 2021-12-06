# server.py
import socket
import sys
from threading import Thread, get_ident
import traceback
import tkinter as tk
from time import sleep
import csv
import pickle

from gui import App


FILENAME = 'data.csv'
PAGE_SIZE = 10


busy_cells = {}
clients_pages = {}

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


def process_query(conn, query, thread_id):
    print(f"Processing query {query[0]} from client {thread_id}")
    '''
    query_dict = {
        'get': send_page(conn, query[1]),
        'edit': check_edit(conn, thread_id, query[1:]),
        'confirm': confirm_edit(conn, thread_id, query[1:]),

    }

    #send_page()
    #print(conn, type(conn))
    #query_dict[query[0]]
    '''
    if query[0] == 'get':
        clients_pages[thread_id] = query[1]
        print(f'{clients_pages=}')
        send_page(conn, query[1])
    elif query[0] == 'edit':
        check_edit(conn, thread_id, query[1:])
    elif query[0] == 'confirm':
        confirm_edit(conn, thread_id, query[1])
    elif query[0] == 'rollback':
        rollback_edit(conn, thread_id)


def rollback_edit(conn, thread_id):
    try:
        cell_id = list(busy_cells.keys())[list(busy_cells.values()).index(thread_id)]
    except ValueError:
        return
    #cell_id = 10 * PAGE_SIZE * coords[0] + 10 * coords[1] + coords[2]

    if busy_cells[cell_id] == thread_id:
        del busy_cells[cell_id]
        send_page(conn, clients_pages[thread_id])


def confirm_edit(conn, thread_id, coords):  #
    #print(coords)
    try:
        cell_id = list(busy_cells.keys())[list(busy_cells.values()).index(thread_id)]
    except ValueError:
        return

    print(f'{cell_id=}')
    print(f'{busy_cells=}')
    print(f'{clients_pages=}')

    #cell_id = 10 * PAGE_SIZE * coords[0] + 10 * coords[1] + coords[2]
    if cell_id in busy_cells:
        if busy_cells[cell_id] == thread_id:
            del busy_cells[cell_id]
            row = cell_id // 10
            col = cell_id % 10
            print(row, col)
            print(data[0])
            data[row][col] = coords
            print(data[0])
            broadcast_page(conn, clients_pages[thread_id])


def check_edit(conn, thread_id, coords):  # проверяет, занята ли клетка: если не занята - занимает
    print(coords)
    cell_id = 10 * PAGE_SIZE * (coords[0]-1) + 10 * coords[1] + coords[2]
    if cell_id not in busy_cells:
        busy_cells[cell_id] = thread_id
        broadcast_page(conn, coords[0])


def broadcast_page(conn, page):  # отправляет страницу всем, кто на ней находится
    rows_from = (page - 1) * PAGE_SIZE + 1
    rows_to = page * PAGE_SIZE + 1
    table = [data[0]]
    table = table + data[rows_from:rows_to]
    # print(table)

    packed_table = pickle.dumps(table)
    conn.sendall(packed_table)
    print('Data sent')


def send_page(conn, page):  # отправляет страницу одному клиенту в ответ на запрос

    rows_from = (page - 1) * PAGE_SIZE + 1
    rows_to = page * PAGE_SIZE + 1
    table = [data[0]]
    table = table + data[rows_from:rows_to]
    print('table=', table)

    packed_table = pickle.dumps(table)
    conn.sendall(packed_table)
    print('Data sent')


def client_thread(conn, ip, port, MAX_BUFFER_SIZE = 4096):

    global number_of_pages
    pages_num = pickle.dumps([number_of_pages])
    conn.sendall(pages_num)

    print(get_ident())

    while True:
        # the input is in bytes, so decode it
        try:
            input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)
        except:
            break

        print('Test')
        # MAX_BUFFER_SIZE is how big the message can be
        # this is test.txt if it's sufficiently big

        siz = sys.getsizeof(input_from_client_bytes)
        if siz >= MAX_BUFFER_SIZE:
            print("The length of input is probably too long: {}".format(siz))

        # decode input and strip the end of line

        input_from_client = pickle.loads(input_from_client_bytes)
        print('Query = ', input_from_client)
        process_query(conn, input_from_client, get_ident())

    conn.close()  # close connection
    # delete busy_cells key
    print('Connection ' + ip + ':' + port + " ended")


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
