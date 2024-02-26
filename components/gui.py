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
        while GUI._is_running:
            await GUI._update()


    @staticmethod
    async def ask_for_model_params():
        model_params = await ainput("Введите параметры модели: Layer_name p1 p2 ")
        batchs_count = await ainput('BATCHS COUNT: ')
        num_epochs = await ainput('EPOCHS: ')
        params = {
                'train_epochs': int(num_epochs),
                'train_batches': int(batchs_count)
                }
        await es.ainvoke('SET_HYPERPARAMS', params)
        await es.ainvoke('ASSEMBLE_MODEL_EVENT', {"model_params": model_params})


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
        GUI._is_running = False
        log('GUI QUIT')

    @staticmethod
    async def _update():
        await GUI._delay()
        # user_input = await ainput()
        # if user_input in ['quit', 'exit']:
        #     await es.ainvoke('APP_QUIT_EVENT', '')
        # else:
        #     log(f'GUI INPUT : {user_input}')
