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
    train_epochs = None
    train_batches = None
    model = None
    
    @staticmethod
    async def _delay():
        delta = time() - Trainer._last_render_time
        delay = max(0, Trainer.max_delay - delta)
        await asyncio.sleep(delay)
        Trainer._last_render_time = time()

    @staticmethod
    @es.subscribe('SET_HYPERPARAMS')
    async def set_hyperparams(hyperparams):
        Trainer.train_epochs = hyperparams["train_epochs"]
        Trainer.train_batches = hyperparams["train_batches"]


    @staticmethod
    @es.subscribe('TRAIN_START_EVENT')
    async def run(model_data):
        Trainer.model = model_data["model"]
        asyncio.get_running_loop().create_task(Trainer.train())


    @staticmethod
    async def train():
        for i in range(Trainer.train_epochs):
            await Trainer.train_epoch()
            await es.invoke("EPOCH_DONE_EVENT", i)

    @staticmethod
    async def train_epoch():
        for i in range(Trainer.train_batches):
            with ProcessPoolExecutor() as pool:
                loop = asyncio.get_running_loop()
                train_batch = partial(Trainer.train_batch, Trainer.model)
                t1 = loop.run_in_executor(pool, train_batch)
                await t1
            await es.invoke("BATCH_DONE_EVENT", i)

    @staticmethod
    def train_batch(model):
        log(f"моделька ({model}) начала считать батч")
        info = sum(i for i in range(100_000_000))
        log("наконец закончила, очень устала")



    @staticmethod
    @es.subscribe('APP_QUIT_EVENT')
    def quit_handler(event_data):
        log(event_data)
        Trainer._is_running = False

    @staticmethod
    async def _update(train_data):
        log(f'[TRAINER UPDATE with data {train_data}]')
        await Trainer._delay()


