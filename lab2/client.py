import os
import socket
import sys
from time import sleep, perf_counter
from threading import Thread, Lock

from config import *

info: dict
mutex = Lock()
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def tf_print():
    while True:
        os.system("clear")
        with mutex:
            progress = int(info['sent_size'] / info['filesize'] * PROGRESS_BAR_SIZE)
            msg = "Info:\n"
            msg += f"\tFilename: {info['filename']}\n"
            msg += f"\tFilesize: {info['filesize']:.2f}\n"
            msg += f"\tSent: {info['sent_size']:.2f}\n"
            msg += f"\tUpload speed: {info['cur_speed']:.2f}\n"
            msg += f"\tAverage speed: {info['avg_speed']:.2f}\n"
            msg += f"\tUpload time: {info['send_time']:.2f}\n"
            msg += f"\tProgress: [{'#'*progress}{'-'*(PROGRESS_BAR_SIZE - progress)}]\n\n"
            print(msg)
        sleep(DELAY)


filename = sys.argv[1]
filesize = os.path.getsize(filename)

info = {
    "filename": filename,
    "filesize": filesize,
    "sent_size": eps,
    "send_time": eps,
    "cur_speed": eps,
    "avg_speed": eps
}

for i in range(3, 0, -1):
    os.system("clear")
    print("Sending file ", filename, " in ", i, " sec")
    sleep(0.5)

client_socket.connect((SERVER_HOST, SERVER_PORT))

th_print = Thread(target=tf_print, daemon=True)
th_print.start()

try:
    client_socket.send((info['filename'] + f' {info["filesize"]}').encode())

    with open(filename, "rb") as file:
        while True:
            data = file.read(SIZE)
            if not data:
                break
            start = perf_counter()
            client_socket.send(data)
            end = perf_counter()
            with mutex:
                info['sent_size'] += len(data)
                info['send_time'] += end - start
                info['cur_speed'] = len(data) / (end - start) / 1024 / 1024 * 8
                info['avg_speed'] = info['sent_size'] / info['send_time']
except KeyboardInterrupt:
    os.system("clear")
    print("Sending cancelled!")
else:
    os.system("clear")
    print("Done!")

client_socket.close()
