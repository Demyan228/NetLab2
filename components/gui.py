import asyncio
from time import time
from common import log
import config
from event_system import EventSystem as es


class GUI:

    _is_running = True
    _last_render_time = time()
    max_delay = 1 / config.FPS
    
    @staticmethod
    async def _delay():
        delta = time() - GUI._last_render_time
        delay = max(0, GUI.max_delay - delta)
        await asyncio.sleep(delay)
        GUI._last_render_time = time()

    @staticmethod
    async def update():
        i = 0
        while GUI._is_running:
            await GUI._update()
            i += 1
            if i == 10:
                await es.ainvoke('TRAIN_START_EVENT', {"epochs": 10, "batches": 5})
        await es.invoke("APP_QUIT_EVENT", {})

    @staticmethod
    @es.subscribe('APP_START_EVENT')
    async def run(_):
        asyncio.get_running_loop().create_task(GUI.update())

    @staticmethod
    @es.subscribe('BATCH_DONE_EVENT')
    async def print_batch_info(bath_count):
        log(f'[{bath_count} BATCH TRAINED')
        await asyncio.sleep(0)

    @staticmethod
    @es.subscribe('APP_QUIT_EVENT')
    async def quit_handler(event_data):
        GUI._is_running = False
        await asyncio.sleep(0)

    @staticmethod
    async def _update():
        log('[GUI UPDATE]')
        await GUI._delay()
