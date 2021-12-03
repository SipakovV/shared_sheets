# server.py
import socket
import sys
from threading import Thread
import traceback
import tkinter as tk
from time import sleep
import csv


FILENAME = 'data.csv'


def read_csv():
    data = []
    with open(FILENAME, newline='') as f:
        reader = csv.reader(f)
        try:
            for row in reader:
                # print(row)
                data.append(row)
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(FILENAME, reader.line_num, e))
    return data
    # print(data)


def do_some_stuffs_with_input(input_string):
    """
    This is where all the processing happens.

    Let's just read the string backwards
    """

    print("Processing that nasty input!")
    return input_string[::-1]


def client_thread(conn, ip, port, MAX_BUFFER_SIZE = 4096):

    # the input is in bytes, so decode it
    input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)

    print('Test')
    # MAX_BUFFER_SIZE is how big the message can be
    # this is test if it's sufficiently big

    siz = sys.getsizeof(input_from_client_bytes)
    if siz >= MAX_BUFFER_SIZE:
        print("The length of input is probably too long: {}".format(siz))

    # decode input and strip the end of line
    input_from_client = input_from_client_bytes.decode("utf8").rstrip()

    res = do_some_stuffs_with_input(input_from_client)
    print("Result of processing {} is: {}".format(input_from_client, res))

    vysl = res.encode("utf8")  # encode the result string
    conn.sendall(vysl)  # send it to client
    conn.close()  # close connection
    print('Connection ' + ip + ':' + port + " ended")


def start_server():

    data = read_csv()
    #print(data)

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
    # not reseting server for every client
    while True:
        conn, addr = soc.accept()
        ip, port = str(addr[0]), str(addr[1])
        print('Accepting connection from ' + ip + ':' + port)
        try:
            Thread(target=client_thread, args=(conn, ip, port)).start()
        except:
            print("Terrible error!")

            traceback.print_exc()
    soc.close()


if __name__ == '__main__':
    start_server()
