import asyncio
from collections import defaultdict
from itertools import count
from dearpygui.dearpygui import Any


def _event_types_generator():
    for idx in count(1):
        yield f'auto_event_type-{idx}'

_uevent_type = _event_types_generator()
def get_event_type():
    return next(_uevent_type)


class EventTypes:
    ASSEMBLE_MODEL = get_event_type()
    APP_QUIT = get_event_type()
    BATCH_DONE = get_event_type()
    EPOCH_DONE = get_event_type()
    START_APP = get_event_type()
    SET_HYPERPARAMS = get_event_type()
    SET_DATASET_PARAMS = get_event_type()
    TRAIN_START = get_event_type()
    TRAINER_QUIT = get_event_type()
    CHANGE_WORKSPACE_WINDOW = get_event_type()


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
            if event_type == EventTypes.APP_QUIT:
                break

    @staticmethod
    async def ainvoke(event_type, event_data: Any = ''):
        await EventSystem.query.put((event_type, event_data))

    @staticmethod
    def invoke(event_type, event_data: Any = ''):
        EventSystem.query.put_nowait((event_type, event_data))

    @staticmethod
    def subscribe(event_type):
        def wrapper(handler):
            EventSystem.subscribers[event_type].append(handler)

            async def inner(*args, **kwargs):
                return await handler(*args, **kwargs)

            return inner

        return wrapper
