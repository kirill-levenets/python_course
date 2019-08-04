

import rabbitpy
import json


class RabbitQueue:
    def __init__(self, host, port, vhost, user, password,
                 exchange_name, queue_name, with_priority=False,
                 queue_mode=None):
        self.host = host
        self.port = port
        self.vhost = vhost
        self.user = user
        self.passwd = password

        self.channel = None
        self.queue = None
        self.exchange = None
        self.connection = None

        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_key = queue_name

        self.connect()

        self.declare_exchange(exchange_name, durable=True)
        self.declare_queue(
            queue_name, durable=True, with_priority=with_priority,
            queue_mode=queue_mode)
        self.bind_queue(exchange_name, routing_key=queue_name)

    def connect(self):
        self.connection = rabbitpy.Connection(
            "{scheme}://{username}:{password}@"
            "{host}:{port}/{virtual_host}".format(
                scheme='amqp',
                username=self.user,
                password=self.passwd,
                host=self.host,
                port=self.port,
                virtual_host=self.vhost))
        self.channel = self.connection.channel()

    def declare_exchange(self, exchange_name, exchange_type='direct',
                         auto_delete=False, durable=False):
        self.exchange = rabbitpy.Exchange(
            self.channel, exchange_name,
            exchange_type=exchange_type, auto_delete=auto_delete,
            durable=durable)

        self.exchange.declare()

    def declare_queue(self, queue_name, auto_delete=False, durable=True,
                      with_priority=False, queue_mode=False):
        arguments = {}
        if with_priority:
            with_priority = int(with_priority)
            arguments = {'x-max-priority': with_priority}

        if queue_mode:  # lazy or other
            arguments.update({'x-queue-mode': queue_mode})

        self.queue = rabbitpy.Queue(
            self.channel, queue_name, auto_delete=auto_delete, durable=durable,
            arguments=arguments)
        self.queue.declare()

    def bind_queue(self, exchange_name, routing_key):
        self.queue.bind(exchange_name, routing_key)

    def publish(self, msg, priority=None):
        self._publish(msg, self.exchange_name, self.routing_key)

    def _publish(self, msg, exchange_name, routing_key, priority=None):
        properties = {'delivery_mode': 2}
        if priority:
            properties['priority'] = priority

        message = rabbitpy.Message(self.channel, msg, properties=properties)
        message.publish(exchange_name, routing_key)

    def start_consuming(self, auto_ack=True, threads=1):
        for message in self.queue.consume(prefetch=threads):
            # lq = len(self.queue)
            # print(lq)
            try:
                if not auto_ack:
                    payload = (json.loads(message.body), message)
                else:
                    payload = json.loads(message.body)
                yield payload
            except Exception as e0:
                print(e0)
                message.nack(requeue=True)
                continue

            if auto_ack:
                message.ack()

            # if lq == 0:
            #     self.stop_consuming()

    def stop_consuming(self):
        try:
            self.queue.stop_consuming()
        except rabbitpy.exceptions.NotConsumingError as e0:
            print(e0)

    def count(self):
        return len(self.queue)


from git_repo.python_course.sug_crawler import sug_config
global_rqueue = RabbitQueue(
    sug_config.RABBIT_HOST, sug_config.RABBIT_PORT, sug_config.RABBIT_VHOST,
    sug_config.RABBIT_USER, sug_config.RABBIT_PASSWORD,
    sug_config.EXCHANGE_NAME, sug_config.QUEUE_NAME)



if __name__ == '__main__':
    from threading import Thread

    def reader(rq: RabbitQueue):
        for msg in rq.start_consuming(threads=100):
            if msg['value'] % 1000 == 0:
                print('read: ', msg)


    def writer(rq: RabbitQueue):
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
    rq_r = RabbitQueue(
        host, port, vhost, user, password, exchange_name, queue_name)

    rq_w = RabbitQueue(
        host, port, vhost, user, password, exchange_name, queue_name)

    t1 = Thread(target=writer, args=(rq_w,))
    t2 = Thread(target=reader, args=(rq_r,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print('finish')
