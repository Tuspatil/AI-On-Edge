"""
This script periodically checks whether scheduler is up
and if not, it will fire up a new vm with a scheduler process
"""
import os
from time import sleep

import socket

import rest_handler


def isOpen(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False


def check_health(service):
    if service.username == "admin":
        return isOpen(service.ip, service.port)
    else:
        # TODO: Hit docker api
        return rest_handler.getContainerStatus(service)
