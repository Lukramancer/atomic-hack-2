from typing import Any, Callable
import aio_pika
from aio_pika import IncomingMessage


class RabbitMQClient:
    def __init__(self, user: str, password: str, host: str, port: str | int, queue_name, logger):
        self._url = f"amqp://{user}:{password}@{host}:{port}/%2F"
        self._queue_name = queue_name
        self._connection = None
        self._channel = None
        self.logger = logger

    async def connect(self):
        self.logger.info(f"Connecting to {self._url}")
        self._connection = await aio_pika.connect_robust(self._url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=1)
        self._queue = await self._channel.declare_queue(self._queue_name, durable=True)

    async def publish_message(self, message: Any):
        if self._channel is None or self._channel.is_closed:
            await self.connect()

        await self._channel.default_exchange.publish(
            aio_pika.Message(body=str(message).encode()),
            routing_key=self._queue_name
        )
        self.logger.info(f"Published message: {message}")

    async def consume_messages(self, process_callable: Callable[[IncomingMessage], Any]):
        if self._channel is None or self._channel.is_closed:
            await self.connect()

        await self._queue.consume(process_callable)
