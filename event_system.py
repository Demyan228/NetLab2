import asyncio
from collections import defaultdict


class EventSystem:

    subscribers = defaultdict(list)
    query = asyncio.Queue()

    @staticmethod
    async def run():
        while True:
            event_type, event_data = await EventSystem.query.get()
            handlers = EventSystem.subscribers[event_type]
            tasks = [handler(event_data) for handler in handlers]
            await asyncio.gather(*tasks)

    @staticmethod
    async def ainvoke(event_type, event_data):
        await EventSystem.query.put((event_type, event_data))

    @staticmethod
    def invoke(event_type, event_data):
        EventSystem.query.put_nowait((event_type, event_data))


    @staticmethod
    def subscribe(event_type):
        def wrapper(handler):
            EventSystem.subscribers[event_type].append(handler)
            async def inner(*args, **kwargs):
                return await handler(*args, **kwargs)
            return inner
        return wrapper
