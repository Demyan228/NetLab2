import asyncio
from time import time
from common import log
import config
from event_system import EventSystem as es
from concurrent.futures import ProcessPoolExecutor
from functools import partial



class Trainer:
    _last_render_time = time()
    _is_running = True
    max_delay = 1 / config.FPS
    
    @staticmethod
    async def _delay():
        delta = time() - Trainer._last_render_time
        delay = max(0, Trainer.max_delay - delta)
        await asyncio.sleep(delay)
        Trainer._last_render_time = time()

    @staticmethod
    @es.subscribe('TRAIN_START_EVENT')
    async def run(train_data):
        asyncio.get_running_loop().create_task(Trainer.train(train_data))

    @staticmethod
    async def train(train_data):
        for i in range(train_data["epochs"]):
            await Trainer.train_epoch(train_data)
            await es.invoke("EPOCH_DONE_EVENT", i)

    @staticmethod
    async def train_epoch(train_data):
        for i in range(train_data["batches"]):
            with ProcessPoolExecutor() as pool:
                loop = asyncio.get_running_loop()
                t1 = loop.run_in_executor(pool, Trainer.train_batch)
                await t1
            await es.invoke("BATCH_DONE_EVENT", i)

    @staticmethod
    def train_batch():
        log("усердно начал считать батч")
        info = sum(i for i in range(100_000_000))
        log("наконец закончил, очень устал")



    @staticmethod
    @es.subscribe('APP_QUIT_EVENT')
    def quit_handler(event_data):
        log(event_data)
        Trainer._is_running = False

    @staticmethod
    async def _update(train_data):
        log(f'[TRAINER UPDATE with data {train_data}]')
        await Trainer._delay()


