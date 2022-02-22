# server.py
import socket
import sys
from threading import Thread, get_ident, enumerate
import traceback
import csv
import pickle
import logging

logging.basicConfig(filename='debug.log', level=logging.DEBUG)



FILENAME = 'data.csv'
PAGE_SIZE = 10
MAX_BUFFER_SIZE = 4096
ADDRESS = ("127.0.0.1", 12345)

busy_cells = {}
clients_pages = {}
client_threads = {}
broadcast_messages = {}
broadcast_indexes = {}

data = []
number_of_pages = 0
row_size = 0


def write_csv():  # запись таблицы в файл .csv
    with open(FILENAME, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)


def read_csv():  # чтение таблицы из файла .csv
    with open(FILENAME, newline='') as f:
        reader = csv.reader(f)
        header_flag = True
        try:
            for row in reader:
                data.append(row)
                if header_flag:
                    global row_size
                    row_size = len(row)
            f.close()
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(FILENAME, reader.line_num, e))
    return data


def process_query(conn, query, thread_id):  # обработка запроса
    if query[0] != 'status':
        logging.debug(f"Processing query {query[0]} from client {thread_id}")
    if query[0] == 'status':
        if len(broadcast_messages) > broadcast_indexes[thread_id]:
            broadcast_status(conn, clients_pages[thread_id], thread_id)
    elif query[0] == 'get':
        clients_pages[thread_id] = query[1]
        if thread_id in busy_cells.values():
            cell_id = list(busy_cells.keys())[list(busy_cells.values()).index(thread_id)]
            del busy_cells[cell_id]
        send_page(conn, query[1])
    elif query[0] == 'edit':
        check_edit(conn, thread_id, query[1:])
    elif query[0] == 'confirm':
        confirm_edit(conn, thread_id, query[1])
    elif query[0] == 'rollback':
        rollback_edit(conn, thread_id)


def rollback_edit(conn, thread_id):  # отмена изменения клетки
    try:
        cell_id = list(busy_cells.keys())[list(busy_cells.values()).index(thread_id)]
    except:
        return

    if busy_cells[cell_id] == thread_id:
        del busy_cells[cell_id]
        row = cell_id // row_size
        col = cell_id % row_size
        broadcast_messages[len(broadcast_messages)] = (None, clients_pages[thread_id], row, col)


def confirm_edit(conn, thread_id, confirmed_value):  # применение изменения в клетке
    try:
        cell_id = list(busy_cells.keys())[list(busy_cells.values()).index(thread_id)]
    except ValueError:
        return

    if cell_id in busy_cells:
        if busy_cells[cell_id] == thread_id:
            del busy_cells[cell_id]
            page = cell_id // (PAGE_SIZE * row_size)
            row = cell_id % (PAGE_SIZE * row_size) // row_size + 1
            col = cell_id % row_size
            data[page*PAGE_SIZE+row][col] = confirmed_value
            broadcast_messages[len(broadcast_messages)] = (confirmed_value, clients_pages[thread_id], row-1, col)
            write_csv()


def check_edit(conn, thread_id, coords):  # проверка, занята ли клетка: если не занята - занять
    cell_id = row_size * PAGE_SIZE * (coords[0]-1) + row_size * coords[1] + coords[2]
    if cell_id not in busy_cells:
        busy_cells[cell_id] = thread_id
        broadcast_messages[len(broadcast_messages)] = (None, coords[0], coords[1], coords[2])


def broadcast_status(conn, page, thread_id):  # отправка изменения на странице в ответ на запрос статуса
    header = data[0]
    modified_cell = ()

    if broadcast_indexes[thread_id] < len(broadcast_messages)+1:
        message = broadcast_messages[broadcast_indexes[thread_id]]
        broadcast_indexes[thread_id] += 1
        if message[1] == page:
            if message[0]:
                modified_cell = (message[2], message[3], message[0])

    in_edit = []
    for key in busy_cells.keys():
        key_page = key // (PAGE_SIZE * row_size)
        key_row = key % (PAGE_SIZE * row_size) // row_size
        key_col = key % row_size
        if page - 1 == key_page:
            in_edit.append((key_row, key_col))

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


def send_page(conn, page):  # отправка всей страницы клиенту в ответ на запрос

    rows_from = (page - 1) * PAGE_SIZE + 1
    rows_to = page * PAGE_SIZE + 1
    header = data[0]
    table = data[rows_from:rows_to]

    in_edit = []
    for key in busy_cells.keys():
        key_page = key // (PAGE_SIZE * row_size)
        key_row = key % (PAGE_SIZE * row_size) // row_size
        key_col = key % row_size
        if page - 1 == key_page:
            in_edit.append((key_row, key_col))

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


def client_thread(conn, ip, port):  # поток, обрабатывающий запросы одного клиента

    global number_of_pages
    pages_num = pickle.dumps([number_of_pages])
    conn.sendall(pages_num)
    broadcast_indexes[get_ident()] = len(broadcast_messages)
    clients_pages[get_ident()] = 1

    while True:
        try:
            try:
                input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)
            except:
                break

            siz = sys.getsizeof(input_from_client_bytes)
            if siz >= MAX_BUFFER_SIZE:
                logging.warning("The length of input is probably too long: {}".format(siz))

            input_from_client = pickle.loads(input_from_client_bytes)
            process_query(conn, input_from_client, get_ident())
        except:
            #traceback.print_exc()
            break

    if get_ident() in busy_cells.values():
        rollback_edit(conn, get_ident())

    conn.close()
    logging.info('Connection ' + ip + ':' + port + " closed")


def start_server():  # запуск сервера
    global data
    global number_of_pages
    data = read_csv()
    number_of_pages = len(data) // PAGE_SIZE + 1

    print('Server started')
    logging.info(f'Csv file read (pages: {number_of_pages}, columns: {row_size})')

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    logging.info('Socket created')

    try:
        soc.bind(ADDRESS)
        #print('Socket bind complete')
    except socket.error:
        logging.error('Bind failed. Error: ' + str(sys.exc_info()))
        sys.exit()

    soc.listen(5)
    logging.info(f'Socket now listening at {ADDRESS[0]}:{ADDRESS[1]}')

    while True:
        try:
            conn, addr = soc.accept()
            ip, port = str(addr[0]), str(addr[1])
            logging.info('Accepting connection from ' + ip + ':' + port)
            print('Accepting connection from ' + ip + ':' + port)
            try:
                Thread(target=client_thread, args=(conn, ip, port), daemon=True).start()
                for thread in enumerate():
                    logging.debug(f'Hello from thread {thread}')
            except:
                print("Terrible error!")
                traceback.print_exc()
        except KeyboardInterrupt:
            logging.info("Server stopped")
            print("\nServer stopped")
            return


if __name__ == '__main__':
    start_server()
