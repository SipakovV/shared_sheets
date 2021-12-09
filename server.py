# server.py
import socket
import sys
from threading import Thread, get_ident, enumerate
import traceback
import tkinter as tk
from time import sleep
import csv
import pickle

from gui import App


FILENAME = 'data.csv'
PAGE_SIZE = 10
MAX_BUFFER_SIZE = 4096

busy_cells = {}
clients_pages = {}
client_threads = {}
broadcast_messages = {}
broadcast_indexes = {}

data = []
number_of_pages = 0
row_size = 0

'''
class ClientThread(Thread):

    def __init__(self, conn, ip, port):
        Thread.__init__(self)
        self.conn = conn
        self.ip = ip
        self.port = port

    def run(self):
        global number_of_pages
        pages_num = pickle.dumps([number_of_pages])
        self.conn.sendall(pages_num)

        print(get_ident())

        while True:
            # the input is in bytes, so decode it
            try:
                input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)
            except:
                print('Got trash from client')
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

        self.conn.close()  # close connection
        # delete busy_cells key
        print('Connection ' + self.ip + ':' + self.port + " ended")

    def update_page(self, page):
        print('Update page at thread #', get_ident())

    #def handle_connection(self, conn, ip, port):


def update_all(page):
    for thread in enumerate():
        if thread is ClientThread:
            thread.update_page(page)
'''


def read_csv():
    with open(FILENAME, newline='') as f:
        reader = csv.reader(f)
        header_flag = True
        try:
            #i = 40
            for row in reader:
                data.append(row)
                if header_flag:
                    global row_size
                    row_size = len(row)
                #i -= 1
                #if i < 0:
                #    break
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
    if query[0] == 'status':
        if len(broadcast_messages) > broadcast_indexes[thread_id]:
            #broadcast_indexes[thread_id] += 1
            broadcast_status(conn, clients_pages[thread_id], thread_id)
    elif query[0] == 'get':
        print(f'{busy_cells=}')
        clients_pages[thread_id] = query[1]
        if thread_id in busy_cells.values():
            cell_id = list(busy_cells.keys())[list(busy_cells.values()).index(thread_id)]
            del busy_cells[cell_id]
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
    except:
        print('Error: busy_cell not found')
        return
    #cell_id = 10 * PAGE_SIZE * coords[0] + 10 * coords[1] + coords[2]

    if busy_cells[cell_id] == thread_id:
        del busy_cells[cell_id]
        row = cell_id // row_size
        col = cell_id % row_size
        broadcast_messages[len(broadcast_messages)] = (None, clients_pages[thread_id], row, col)
        #broadcast_status(conn, clients_pages[thread_id])
        print(f'{broadcast_messages=}')


def confirm_edit(conn, thread_id, confirmed_value):  #
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
            page = cell_id // (PAGE_SIZE * row_size)
            row = cell_id % (PAGE_SIZE * row_size) // row_size + 1
            col = cell_id % row_size
            #print(row, col)
            #print(data[0])
            data[page*PAGE_SIZE+row][col] = confirmed_value
            #print(data[0])
            #broadcast_page(conn, clients_pages[thread_id], (row, col, confirmed_value))
            broadcast_messages[len(broadcast_messages)] = (confirmed_value, clients_pages[thread_id], row-1, col)
            print(f'{broadcast_messages=}')
            #send_page(conn, clients_pages[thread_id])


def check_edit(conn, thread_id, coords):  # проверяет, занята ли клетка: если не занята - занимает
    print(coords)
    cell_id = row_size * PAGE_SIZE * (coords[0]-1) + row_size * coords[1] + coords[2]
    if cell_id not in busy_cells:
        busy_cells[cell_id] = thread_id
        broadcast_messages[len(broadcast_messages)] = (None, coords[0], coords[1], coords[2])
        print(f'{broadcast_messages=}')
        #send_page(conn, coords[0])


def broadcast_status(conn, page, thread_id):  # отправляет страницу всем, кто на ней находится


    rows_from = (page - 1) * PAGE_SIZE + 1
    rows_to = page * PAGE_SIZE + 1
    header = data[0]
    table = data[rows_from:rows_to]
    # print('table=', table)
    modified_cell = ()

    if broadcast_indexes[thread_id] < len(broadcast_messages)+1:
        message = broadcast_messages[broadcast_indexes[thread_id]]
        broadcast_indexes[thread_id] += 1
        if message[1] == page:
            if message[0]:
                modified_cell = (message[2], message[3], message[0])
                print('CELL MODIFIED')

    print(f'{modified_cell=}')

    in_edit = []
    for key in busy_cells.keys():
        key_page = key // (PAGE_SIZE * row_size)
        key_row = key % (PAGE_SIZE * row_size) // row_size
        key_col = key % row_size
        if page - 1 == key_page:
            in_edit.append((key_row, key_col))

    print(f'{in_edit=}')

    data_dict = {
        'type': 'part',
        'modified': modified_cell,
        'header': header,
        'edit': in_edit,
        'page_num': page,
        'filename': FILENAME,
        'page_size': PAGE_SIZE,
        'row_size': row_size,
    }

    packed_data = pickle.dumps(data_dict)
    conn.sendall(packed_data)
    print('Status sent')


def send_page(conn, page):  # отправляет страницу одному клиенту в ответ на запрос

    rows_from = (page - 1) * PAGE_SIZE + 1
    rows_to = page * PAGE_SIZE + 1
    header = data[0]
    table = data[rows_from:rows_to]
    #print('table=', table)

    in_edit = []
    for key in busy_cells.keys():
        key_page = key // (PAGE_SIZE * row_size)
        key_row = key % (PAGE_SIZE * row_size) // row_size
        key_col = key % row_size
        if page - 1 == key_page:
            in_edit.append((key_row, key_col))

    print(f'{in_edit=}')

    data_dict = {
        'type': 'full',
        'table': table,
        'header': header,
        'edit': in_edit,
        'page_num': page,
        'filename': FILENAME,
        'page_size': PAGE_SIZE,
        'row_size': row_size,
    }

    packed_data = pickle.dumps(data_dict)
    conn.sendall(packed_data)
    print('Data sent')


def client_thread(conn, ip, port, MAX_BUFFER_SIZE = 4096):

    global number_of_pages
    pages_num = pickle.dumps([number_of_pages])
    conn.sendall(pages_num)

    broadcast_indexes[get_ident()] = 0

    print(get_ident())


    while True:
        try:
        # the input is in bytes, so decode it
            try:
                input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)
            except:
                break

            #print('Test')
            # MAX_BUFFER_SIZE is how big the message can be
            # this is test.txt if it's sufficiently big

            siz = sys.getsizeof(input_from_client_bytes)
            if siz >= MAX_BUFFER_SIZE:
                print("The length of input is probably too long: {}".format(siz))

            # decode input and strip the end of line

            input_from_client = pickle.loads(input_from_client_bytes)
            print('Query = ', input_from_client)
            process_query(conn, input_from_client, get_ident())
        except:
            traceback.print_exc()
            break

    conn.close()  # close connection
    # delete busy_cells key
    print('Connection ' + ip + ':' + port + " ended")


def start_server():
    global data
    global number_of_pages
    data = read_csv()
    number_of_pages = len(data) // PAGE_SIZE + 1

    print(f'Csv file read (pages: {number_of_pages}, columns: {row_size})')

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
        print('Before accept')
        conn, addr = soc.accept()
        print('After accept')
        ip, port = str(addr[0]), str(addr[1])
        print('Accepting connection from ' + ip + ':' + port)
        try:
            Thread(target=client_thread, args=(conn, ip, port), daemon=True).start()

            #client_threads[(ip, port)] = ClientThread(conn, ip, port)
            #client_threads[(ip, port)].handle_connection(conn, ip, port)
            #client_threads[(ip, port)].setDaemon(True)
            #client_threads[(ip, port)].start()
            for thread in enumerate():
                print(f'hello from thread {thread}')
            #update_all(1)
            #client_threads[(ip, port)].update_page(1)

        except:
            print("Terrible error!")
            traceback.print_exc()
    soc.close()


if __name__ == '__main__':
    start_server()
