
import rabbitpy
import json
import logging
from multiprocessing import current_process

from sug_config import (RABBIT_HOST, RABBIT_PORT, RABBIT_VHOST,
RABBIT_USER, RABBIT_PASSWORD, EXCHANGE_NAME, QUEUE_NAME, ROUTING_KEY)


class RabbitManager:
    def __init__(self, with_priority=False, queue_mode=None):
        self._log = logging.getLogger(current_process().name)
        self._host = RABBIT_HOST
        self._port = RABBIT_PORT
        self._vhost = RABBIT_VHOST
        self._user = RABBIT_USER
        self._passwd = RABBIT_PASSWORD

        self._channel = None
        self._queue = None
        self._exchange = None
        self._connection = None

        self._exchange_name = EXCHANGE_NAME
        self._queue_name = QUEUE_NAME
        self._routing_key = ROUTING_KEY

        self._connect()

        self._declare_exchange(EXCHANGE_NAME, durable=True)
        self._declare_queue(
            QUEUE_NAME, durable=True, with_priority=with_priority,
            queue_mode=queue_mode)
        self._bind_queue(EXCHANGE_NAME, routing_key=ROUTING_KEY)

    def _connect(self):
        self._connection = rabbitpy.Connection(
            "{scheme}://{username}:{password}@"
            "{host}:{port}/{virtual_host}".format(
                scheme='amqp',
                username=self._user,
                password=self._passwd,
                host=self._host,
                port=self._port,
                virtual_host=self._vhost))
        self._channel = self._connection.channel()

    def _declare_exchange(self, exchange_name, exchange_type='direct',
                          auto_delete=False, durable=False):
        self._exchange = rabbitpy.Exchange(
            self._channel, exchange_name,
            exchange_type=exchange_type, auto_delete=auto_delete,
            durable=durable)

        self._exchange.declare()

    def _declare_queue(self, queue_name, auto_delete=False, durable=True,
                       with_priority=False, queue_mode=False):
        arguments = {}
        if with_priority:
            with_priority = int(with_priority)
            arguments = {'x-max-priority': with_priority}

        if queue_mode:  # lazy or other
            arguments.update({'x-queue-mode': queue_mode})

        self._queue = rabbitpy.Queue(
            self._channel, queue_name, auto_delete=auto_delete, durable=durable,
            arguments=arguments)
        self._queue.declare()

    def _bind_queue(self, exchange_name, routing_key):
        self._queue.bind(exchange_name, routing_key)

    def publish(self, msg, priority=None):
        self._publish(msg, self._exchange_name, self._routing_key)

    def _publish(self, msg, exchange_name, routing_key, priority=None):
        properties = {'delivery_mode': 2}
        if priority:
            properties['priority'] = priority

        message = rabbitpy.Message(self._channel, msg, properties=properties)
        message.publish(exchange_name, routing_key)

    def get(self):
        val = None
        try:
            val = self._queue.get(acknowledge=False)
        except Exception as e0:
            self._log.debug(e0)
        return val

    def stop_consuming(self):
        try:
            self._queue.stop_consuming()
        except rabbitpy.exceptions.NotConsumingError as e0:
            print(e0)

    def count(self):
        return len(self._queue)


global_rqueue = RabbitManager()


if __name__ == '__main__':
    from threading import Thread

    def reader(rq: RabbitManager):
        for msg in rq.start_consuming(threads=100):
            if msg['value'] % 1000 == 0:
                print('read: ', msg)


    def writer(rq: RabbitManager):
        message = {'value': 0}
        for i in range(50_000):
            message['value'] = i
            if i % 1000 == 0:
                print('publish: ', i)
            rq.publish(
                message, exchange_name, queue_name)

    host = 'localhost'
    port = 5672
    vhost = '/'
    user, password = 'guest', 'guest'
    exchange_name, queue_name = 'test_exchange', 'test_queue'
    rq_r = RabbitManager(
        host, port, vhost, user, password, exchange_name, queue_name)

    rq_w = RabbitManager(
        host, port, vhost, user, password, exchange_name, queue_name)

    t1 = Thread(target=writer, args=(rq_w,))
    t2 = Thread(target=reader, args=(rq_r,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print('finish')
