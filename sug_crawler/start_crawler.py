

import logging
import sys
from threading import Event
from multiprocessing import current_process
from libs.async_crawler import AsyncCrawler


if __name__ == '__main__':

    # init logger
    # print(current_process().name)
    logger = logging.getLogger(current_process().name)
    logger.setLevel(logging.DEBUG)

    log_formatter = logging.Formatter(
        '[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} '
        '%(levelname)s - %(message)s'
    )

    file_handler = logging.FileHandler(
        'logs/crawler.log', mode='a', encoding='utf8')
    file_handler.setFormatter(log_formatter)

    s_handler = logging.StreamHandler(sys.stdout)
    s_handler.setFormatter(log_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(s_handler)


    ee = Event()
    daemon = AsyncCrawler(exit_event=ee)
    daemon.run()
