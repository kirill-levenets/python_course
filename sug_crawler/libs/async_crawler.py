import json
import random
from threading import Event
import asyncio
import aiosqlite
from aiohttp import ClientSession
from aiosocksy.connector import ProxyConnector, ProxyClientRequest

import queue
import datetime

import logging
from multiprocessing import current_process

from sug_config import (URL, HEADERS, MAX_INNER_QUEUE_SIZE, DB_NAME,
    MAX_ERRORS_COUNT)
from libs.proxy_manager import ProxyManager
from libs.rabbit_manager import RabbitManager


class AsyncCrawler:
    def __init__(self, exit_event):
        self.exit_event = exit_event
        self.loop = asyncio.get_event_loop()
        self.queue_from_web = RabbitManager()
        self.inner_queue = queue.Queue()
        self.proxy_manager = ProxyManager()
        print(current_process().name)
        self.log = logging.getLogger(current_process().name)

        self.url = URL
        self.headers = HEADERS
        self.connect = None

        self.workers_count = 1
        for w_num in range(self.workers_count):
            self.loop.create_task(self.fetch(w_num))

        self.loop.create_task(self.listener())
        self.loop.create_task(self.init_db())
        self.log.info('crawler inited')

    def run(self):
        self.log.info('crawler run')
        self.loop.run_forever()

    async def listener(self):
        self.log.info('crawler rabbit listener started')
        while not self.exit_event.is_set():
            if self.inner_queue.qsize() > MAX_INNER_QUEUE_SIZE:
                await asyncio.sleep(0.1)
                continue

            web_task = self.queue_from_web.get()
            if web_task:
                self.inner_queue.put(web_task)
            else:
                await asyncio.sleep(0.5)
                if random.randint(1, 10) == 2:
                    self.log.debug('rabbit queue is empty')

    async def init_db(self):
        self.log.info('crawler init_db started')

        self.connect = await aiosqlite.connect(DB_NAME)

        # await self.connect.execute('''drop table IF EXISTS keywords;''')
        # await self.connect.commit()

        await self.connect.execute(
            '''CREATE TABLE IF NOT EXISTS keywords(
                keyword_id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword CHAR(128) UNIQUE NOT NULL);
            ''')
        await self.connect.commit()

        cur = await self.connect.execute('select keyword from keywords limit 100')
        self.log.debug(await cur.fetchall())
        # self.loop.stop()

    async def stop(self):
        await self.cursor.close()
        await self.connect.close()
        self.loop.close()

    async def write_to_db(self, suggestions):
        self.log.info('crawler write_to_db')
        s = ', '.join(['(?)' for sg in suggestions])
        await self.connect.execute(
            'INSERT OR IGNORE INTO keywords(keyword) VALUES {s}'.format(
                s=s), suggestions)
        self.log.debug("rows saved: {}".format(self.connect.total_changes))
        await self.connect.commit()
        # self.cursor = await self.connect.execute('SELECT * FROM some_table')
        # rows = await self.cursor.fetchall()

    async def fetch(self, worker_id):
        self.log.info(f'[{worker_id}]: crawler fetch')
        # proxy_connector = ProxyConnector(
        #     remote_resolve=False,
        #     enable_cleanup_closed=True,
        #     force_close=True,
        #     limit=300
        # )
        async with ClientSession() as session:
            while not self.exit_event.is_set():
                try:
                    web_task = self.inner_queue.get_nowait()
                except queue.Empty:
                    await asyncio.sleep(0)
                    continue
                # proxy = self.proxy_manager.next_proxy()

                # proxy_str = "http://{}".format(proxy)

                # proxy_auth = None

                # session._coonector = proxy_connector
                # session._cookie_jar.clear()
                # session._cookie_jar.update_cookies({})
                # session._request_class = ProxyClientRequest

                web_task_dict = json.loads(web_task.body)
                query = web_task_dict['keyword']
                self.log.debug(self.url.format(query=query))
                try:
                    async with session.get(
                            url=self.url.format(query=query),
                            # proxy=proxy_str,
                            # headers=self.headers,
                            timeout=3,
                            # compress=True,
                            # proxy_auth=proxy_auth,
                            allow_redirects=True) as response:
                        self.log.debug(f"[{worker_id}]: {response}")
                        txt = await response.read()
                        txt = str(txt, 'utf8')
                        txt = txt.replace(
                            'autocompleteCallback(', '').replace(');', '')
                        phrases = eval(txt)
                        phrases = [d['phrase'] for d in phrases]
                        if phrases:
                            await self.write_to_db(phrases)
                        # web_task.ack()
                except (asyncio.TimeoutError, OSError) as e0:
                    self.log.warning('[{}]: {}: Error: {}, for {}\n'.format(
                        worker_id, datetime.datetime.now(), e0, 'proxy'))
                    self.queue_from_web.publish(web_task_dict)
                except Exception as e0:
                    self.log.warning('[{}]: {}: Exception for {}\n'.format(
                        worker_id, datetime.datetime.now(), 'proxy'))
                    self.log.exception(e0, exc_info=True)

                    if web_task_dict.get('ttl', 0) < MAX_ERRORS_COUNT:
                        web_task_dict['ttl'] = web_task_dict.get('ttl', 0) + 1
                        self.queue_from_web.publish(web_task_dict)


if __name__ == '__main__':
    ee = Event()
    daemon = AsyncCrawler(exit_event=ee)
    daemon.run()
