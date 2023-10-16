import ipaddress
import time
import uuid
import sys
import os
from colorama import Fore, Back, Style
from scapy.all import *
from threading import Thread, Lock

SNIFF_TIMEOUT = 1
PRINT_TIME = 1

IP4 = "IPv4"
IP6 = "IPv6"
NMG = "Not a multicast group"
INVIP = "Invalid IP"

app_uid = str(uuid.uuid4())
app_list = list()

mutex = Lock()

def ping_multicast(ip_addr, port_addr):
    pack = IP(
        dst = ip_multicast
    ) / UDP (
        dport = int(port_multicast)
    ) / app_uid.encode("utf-8")

    send(pack, verbose=False)


def packet_handler(packet):
    if UDP in packet:
        payload = packet[Raw].load.decode("utf-8")
        if payload != f"{app_uid}":
            with mutex:
                app_list.append(payload)


def sniffer_multicast(ip_addr, port_addr):
    with mutex:
        app_list.clear()

    packet = sniff(
        filter="udp and dst port " + str(port_addr),
        prn=packet_handler, 
        timeout=SNIFF_TIMEOUT
    )


def check_multicast_group(ip_multicast):
    try:
        ip = ipaddress.ip_address(ip_multicast)
        if ip.version == 4 and ip.is_multicast:
            return "IPv4"
        if ip.version == 6 and ip.is_multicast:
            return "IPv6"
        return "Not a multicast group"
    except ValueError:
        return "Invalid IP"


# def check_multicast_port(port_multicast):
#     try:
#         pass
#     except ValueError:
#         pass


def tf_ping():
    while True:
        ping_multicast(ip_multicast, port_multicast)


def tf_sniff():
    while True:
        sniffer_multicast(ip_multicast, port_multicast)


ip_multicast = sys.argv[1]
port_multicast = 12345

protocol = check_multicast_group(ip_multicast)
if protocol == NMG or protocol == INVIP:
    print(protocol)
    exit()


if __name__ == "__main__":
    print(f"{Fore.CYAN}App UID: {app_uid}{Fore.RESET} started ->")

    th_ping = Thread(target=tf_ping, daemon=True)
    th_sniff = Thread(target=tf_sniff, daemon=True)

    th_ping.start()
    th_sniff.start()

    try:
        while True:
            os.system("clear")
            with mutex:
                app_set = set(app_list)
                if len(app_set) > 1:
                    me = app_uid[-len(app_list[0]):]
                    if me in app_set:
                        app_set.remove(me)
                    res = " - " + "\n - ".join(app_set)
                    print(res)
                    print("\nMy UID: ", app_uid)
                    print("\nmy short UID: ", me)
                else:
                    print("No copies")
            time.sleep(PRINT_TIME)
    except KeyboardInterrupt:
        exit()
