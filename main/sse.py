import asyncio
from collections import defaultdict

class BookingEventHub:
    """
    Fan-out hub for chat rooms (MVP-grade, no Redis).
    Each room has its own set of asyncio.Queue listeners.
    """
    def __init__(self):
        self.room_connections = defaultdict(set)

    def register(self, chat_id: int) -> asyncio.Queue:
        q = asyncio.Queue()
        self.room_connections[chat_id].add(q)
        return q

    def unregister(self, chat_id: int, q: asyncio.Queue):
        self.room_connections[chat_id].discard(q)
        if not self.room_connections[chat_id]:
            del self.room_connections[chat_id]

    async def push(self, chat_id: int, data: dict):
        print(data)
        dead = set()
        for q in self.room_connections.get(chat_id, []):
            try:
                await q.put(data)
            except Exception:
                dead.add(q)
        for dq in dead:
            self.room_connections[chat_id].discard(dq)
# singleton the rest of the code imports
booking_events = BookingEventHub()

