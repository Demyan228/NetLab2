import asyncio
from time import time
from common import log
import config
from event_system import EventSystem as es
from aioconsole import ainput


class GUI:

    _is_running = True
    _last_render_time = time()
    max_delay = 1 / config.FPS
    model_params = None
    is_train_start = False
    
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
            if GUI.model_params is not None and not GUI.is_train_start:
                GUI.is_train_start = True
                await es.invoke('SET_HYPERPARAMS', {"train_epochs":5, "train_batches":10})
                await es.invoke('ASSEMBLE_MODEL_EVENT', {"model_params": GUI.model_params})
            if GUI.is_train_start:
                log('[GUI UPDATE]')



    @staticmethod
    async def ask_for_model_params():
        inp = await ainput("Введите параметры модели: Layer_name p1 p2 ")
        GUI.model_params = inp.split()


    @staticmethod
    @es.subscribe('APP_START_EVENT')
    async def run(_):
        loop = asyncio.get_running_loop()
        loop.create_task(GUI.update())
        loop.create_task(GUI.ask_for_model_params())

    @staticmethod
    @es.subscribe('BATCH_DONE_EVENT')
    async def print_batch_info(bath_count):
        log(f'[{bath_count} BATCH TRAINED')
        await asyncio.sleep(0)

    @staticmethod
    @es.subscribe('APP_QUIT_EVENT')
    async def quit_handler(event_data):
        log(event_data)
        GUI._is_running = False
        await asyncio.sleep(0)

    @staticmethod
    async def _update():
        #log('[GUI UPDATE]')
        await GUI._delay()
