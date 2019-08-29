
import heapq
import os
import time
import logging
from multiprocessing import current_process

from sug_config import PROXY_FILE_PATH



class Proxy:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.can_use_time = time.time()
        self.counter = 0
        self.status = 'n/a'

    def __lt__(self, other):
        return self.can_use_time < other.can_use_time

    def __repr__(self):
        return '{}:{} [{} - {} - {}]'.format(
            self.ip, self.port, self.counter, self.can_use_time, self.status
        )

    def __str__(self):
        return '{}:{}'.format(self.ip, self.port)


class ProxyManager:
    def __init__(self, ok_timeout=1, ban_timeout=10):
        self.proxies = self.read_file()
        self.ok_proxies = [Proxy(ip, port) for ip, port in self.proxies]
        self.log = logging.getLogger(current_process().name)
        heapq.heapify(self.ok_proxies)
        self.ban_proxies = []
        heapq.heapify(self.ban_proxies)
        self.ban_timeout = ban_timeout
        self.ok_timeout = ok_timeout
        self.log.debug(f'{self.ok_proxies}\n{self.ban_proxies}')

    def read_file(self):
        with open(PROXY_FILE_PATH, 'r') as f:
            proxies = [s.strip().split(':') for s in f.readlines()]
        return proxies

    def next_proxy(self):
        cur_time = time.time()
        can_use_time = cur_time * 10

        if self.ok_proxies:
            new_proxy: Proxy = heapq.heappop(self.ok_proxies)
            can_use_time = new_proxy.can_use_time
        elif self.ban_proxies:
            new_proxy = heapq.heappop(self.ban_proxies)
            can_use_time = new_proxy.can_use_time
        else:
            self.log.debug('ok and ban are empty!')

        if can_use_time < cur_time:
            return new_proxy

        raise IndexError('no proxies left')

    def back_proxy(self, proxy: Proxy, response: str):
        proxy.counter += 1
        proxy.status = response
        self.log.debug(f'back: {proxy}')
        if response == 'ok':
            proxy.can_use_time = time.time() + self.ok_timeout
            heapq.heappush(self.ok_proxies, proxy)
        else:
            proxy.can_use_time = time.time() + self.ban_timeout
            heapq.heappush(self.ban_proxies, proxy)
            # self.log.debug(f'{self.ok_proxies}\n{self.ban_proxies}')

    def proxy_generator(self):
        while True:
            try:
                yield self.next_proxy()
            except:
                time.sleep(0.1)



if __name__ == '__main__':
    p = ProxyManager()
    pg = p.proxy_generator()
    for i in range(10):
        print(i)
        np = next(pg)
        print(np)
        time.sleep(1)
        p.back_proxy(np, 'ok' if i % 2 == 0 else 'ban')


    for key, value in p.ok_proxies + p.ban_proxies:
        print('Ip: {}, Port: {}, Date: {}, Counter: {}, '
              'Status: {}, '.format(key, value[0],
                                    value[1], value[2], value[3]))

    print('finish')
