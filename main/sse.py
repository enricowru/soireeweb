import asyncio

class BookingEventHub:
    """
    In‑memory fan‑out hub (MVP‑grade, no Redis).
    Each listener gets its own asyncio.Queue.
    """
    def __init__(self):
        self.connections: set[asyncio.Queue] = set()

    def register(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self.connections.add(q)
        return q

    async def push(self, data: dict):
        dead = set()
        for q in self.connections:
            try:
                await q.put(data)
            except Exception:
                dead.add(q)
        self.connections -= dead


# singleton the rest of the code imports
booking_events = BookingEventHub()
