import socket
from time import perf_counter, sleep
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Lock
import os
import sys

from config import *

mutex = Lock()

MAX_USERS = 4

client_map = dict()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(MAX_USERS)


def serve_client(cl_sock: socket.socket, cl_addr: any) -> None:
    filename, filesize = cl_sock.recv(SIZE).decode().split(" ")
    filesize = float(filesize)
    with mutex:
        client_map[cl_addr] = {
            "filename": filename,
            "filesize": filesize,
            "recv_size": eps,
            "recv_time": eps,
            "cur_speed": eps,
            "avg_speed": eps
        }
    with open("./" + DOWNLOADS + "/" + filename, "wb") as file:
        while True:
            start = perf_counter()
            data = cl_sock.recv(SIZE)
            end = perf_counter()
            if not data:
                break
            with mutex:
                client = client_map[cl_addr]
                client["recv_size"] += len(data)
                client["recv_time"] += end - start
                client["cur_speed"] = len(data) / (end - start) / 1024 / 1024 * 8
                client["avg_speed"] = client["recv_size"] / client["recv_time"] / 1024 / 1024 * 8
            file.write(data)
    with mutex:
        del client_map[cl_addr]
    cl_sock.close()


def tf_print():
    while True:
        os.system("clear")
        with mutex:
            if not client_map:
                print("No clients")
            else:
                print("Clients: ")
                for cl_addr, client in client_map.items():
                    progress = int(client['recv_size'] / client['filesize'] * PROGRESS_BAR_SIZE)
                    msg = f" - {cl_addr[0]}, {cl_addr[1]}:\n"
                    msg += f"\tFilename: {client['filename']}\n"
                    msg += f"\tFilesize: {client['filesize']:.2f}\n"
                    msg += f"\tRecieved: {client['recv_size']:.2f}\n"
                    msg += f"\tDownload speed: {client['cur_speed']:.2f}\n"
                    msg += f"\tAverage speed: {client['avg_speed']:.2f}\n"
                    msg += f"\tDownload time: {client['recv_time']:.2f}\n"
                    msg += f"\tProgress: [{'#'*progress}{'-'*(PROGRESS_BAR_SIZE - progress)}]\n\n"
                    print(msg)
        sleep(DELAY)


th_print = Thread(target=tf_print, daemon=True)
th_print.start()

try:
    while True:
        client_socket, client_addr = server_socket.accept()
        Thread(
            target=serve_client,
            args=(client_socket, client_addr),
            daemon=True
        ).start()
except KeyboardInterrupt:
    server_socket.close()
