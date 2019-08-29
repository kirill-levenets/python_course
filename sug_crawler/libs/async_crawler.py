import asyncio
import datetime
import json
import logging
import queue
import random
from multiprocessing import current_process

import asyncpg
from aiohttp import ClientSession
from aiosocksy.connector import ProxyConnector, ProxyClientRequest

from libs.proxy_manager import ProxyManager
from libs.rabbit_manager import RabbitManager
from sug_config import (
    URL, HEADERS, MAX_INNER_QUEUE_SIZE, DB_NAME, MAX_ERRORS_COUNT,
    NUM_WORKERS, PROXY_OK_TIMEOUT, PROXY_BN_TIMEOUT)


class AsyncCrawler:
    def __init__(self, exit_event):
        self.exit_event = exit_event
        self.loop = asyncio.get_event_loop()
        self.queue_from_web = RabbitManager()
        self.inner_queue = queue.Queue()
        self.proxy_manager = ProxyManager(
            ok_timeout=PROXY_OK_TIMEOUT, ban_timeout=PROXY_BN_TIMEOUT)
        self.log = logging.getLogger(current_process().name)

        self.url = URL
        self.headers = HEADERS
        self.connect = None

        self.db_pool = self.loop.run_until_complete(
            asyncpg.create_pool(DB_NAME))

        self.workers_count = NUM_WORKERS
        for w_num in range(self.workers_count):
            self.loop.create_task(self.fetch(w_num))

        self.loop.create_task(self.listener())
        self.log.info('crawler inited')


    def run(self):
        self.log.info('crawler run')
        self.loop.run_forever()

    async def listener(self):
        self.log.info('crawler rabbit listener started')
        while not self.exit_event.is_set():
            if self.inner_queue.qsize() > MAX_INNER_QUEUE_SIZE:
                # self.log.debug(
                #     f'listener: {self.inner_queue.qsize()} | '
                #     f'{self.queue_from_web.count()}')
                await asyncio.sleep(0.1)
                continue

            web_task = self.queue_from_web.get()
            if web_task:
                self.inner_queue.put(web_task)
            else:
                await asyncio.sleep(0.5)
                if random.randint(1, 10) == 2:
                    self.log.debug('rabbit queue is empty')

    async def stop(self):
        # await self.cursor.close()
        # await self.connect.close()
        self.loop.close()

    async def write_to_db(self, suggestions):
        self.log.info('crawler write_to_db')
        # s = ', '.join(['(?)' for sg in suggestions])
        # await self.connect.execute(
        #     'INSERT IGNORE INTO keywords(keyword) VALUES {s}'.format(
        #         s=s), suggestions)

        s = ', '.join([f'(${i + 1})' for i in range(len(suggestions))])
        res = None
        try:
            async with self.db_pool.acquire() as conn:
                res = await conn.execute(
                    f'''INSERT INTO keywords (keyword) 
                    VALUES {s}
                    RETURNING keyword_id''', *suggestions)

        except asyncpg.IntegrityConstraintViolationError as e:
            self.log.debug(e)

        self.log.debug("rows saved: {}".format(res))

    async def fetch(self, worker_id):
        self.log.info(f'[{worker_id}]: crawler fetch')

        proxy_connector = ProxyConnector(
            remote_resolve=False,
            enable_cleanup_closed=True,
            force_close=True,
            limit=300
        )

        async with ClientSession() as session:
            while not self.exit_event.is_set():
                try:
                    web_task = self.inner_queue.get_nowait()
                except queue.Empty:
                    await asyncio.sleep(0)
                    continue

                while not self.exit_event.is_set():
                    try:
                        proxy = self.proxy_manager.next_proxy()
                        self.log.debug(f'[{worker_id}] got {proxy}')
                        break
                    except IndexError as e:
                        self.log.debug(e)
                        await asyncio.sleep(0.0)

                proxy_str = "http://{}".format(proxy)
                proxy_auth = None
                session._coonector = proxy_connector
                session._cookie_jar.clear()
                session._cookie_jar.update_cookies({})
                session._request_class = ProxyClientRequest

                web_task_dict = json.loads(web_task.body)
                query = web_task_dict['keyword']
                self.log.debug(self.url.format(query=query))
                proxy_response = False
                try:
                    async with session.get(
                            url=self.url.format(query=query),
                            proxy=proxy_str,
                            headers=self.headers,
                            timeout=30,
                            compress=True,
                            proxy_auth=proxy_auth,
                            allow_redirects=True) as response:
                        self.log.debug(f"[{worker_id}]: {response}")
                        txt = await response.read()
                        txt = str(txt, 'utf8')
                        self.log.debug(f"[{worker_id}]: {txt}")
                        txt = txt.replace(
                            'autocompleteCallback(', '').replace(');', '')
                        phrases = eval(txt)
                        phrases = [d['phrase'] for d in phrases]
                        self.log.debug(f"[{worker_id}]: {phrases}")
                        if phrases:
                            await self.write_to_db(phrases)
                        proxy_response = True
                except (asyncio.TimeoutError, OSError) as e0:
                    self.log.warning('[{}]: {}: Error: {}, for {}\n'.format(
                        worker_id, datetime.datetime.now(), repr(e0), 'proxy'))
                    self.queue_from_web.publish(web_task_dict)
                except Exception as e0:
                    self.log.warning('[{}]: {}: Exception for {}\n'.format(
                        worker_id, datetime.datetime.now(), 'proxy'))
                    self.log.exception(e0, exc_info=True)

                    if web_task_dict.get('ttl', 0) < MAX_ERRORS_COUNT:
                        web_task_dict['ttl'] = web_task_dict.get('ttl', 0) + 1
                        self.queue_from_web.publish(web_task_dict)
                finally:
                    # web_task.ack()
                    self.proxy_manager.back_proxy(proxy, proxy_response)
