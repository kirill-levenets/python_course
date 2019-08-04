
'''
TODO: *
'''
import logging


def init_log():
    pass


class DaemonCrawler:
    '''
    Listen to rabbit queue.
    get task. generates futures to loop with requests to google.
    uses proxie
    '''
    def __init__(self, config):
        self.config = config

