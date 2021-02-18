# -*- coding: utf-8 -*-
import socket
import time
from collections import defaultdict


class ClientError(Exception):
    pass


class Client:

    def __init__(self, ip, port, timeout=None):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.buffer_size = 1024

    def put(self, metric_name, metric_value, timestamp=None):
        if not timestamp:
            timestamp = str(int(time.time()))
        else:
            timestamp = str(timestamp)
        timestamp += '\n'
        metric_value = str(metric_value)

        message = ' '.join(['put', metric_name, metric_value, timestamp])

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.ip, self.port))
            sock.settimeout(self.timeout)
            sock.send(message.encode())
            data = sock.recv(self.buffer_size).decode()

        if data == 'error\nwrong command\n\n':
            raise ClientError()

    def get(self, metric_name):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.ip, self.port))
            sock.settimeout(self.timeout)
            key = 'get {}\n'.format(metric_name)
            sock.send(key.encode())
            data = sock.recv(self.buffer_size).decode()

        if data == 'ok\n\n':
            return {}
        if data == 'error\nwrong command\n\n':
            raise ClientError()

        metric_items = data.lstrip('ok\n').rstrip('\n\n')
        metric_items = [x.split() for x in metric_items.split('\n')]

        metric_dict = defaultdict(list)
        for key, metric, timestamp in metric_items:
            metric_dict[key].append((int(timestamp), float(metric)))

        return metric_dict
