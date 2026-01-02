import queue
from app.services.queue.base import MessageQueue

class FakeQueue(MessageQueue):
    def __init__(self):
        self._queue = queue.Queue()
    
    def publish(self, message: dict) -> None:
        self._queue.put(message)
    
    def consume(self) -> dict:
        return self._queue.get()