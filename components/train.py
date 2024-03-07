import asyncio
from time import time
from common import log
import config
from event_system import EventSystem as es
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Optional
import torch


class NotInitializedError(Exception): ...

class Trainer:
    _last_render_time = time()
    _is_running = True
    max_delay = 1 / config.FPS
    train_epochs: int = 0
    train_batches: int = 0
    learning_rate: int = 0
    model = None
    _is_initialized = False

    @staticmethod
    @es.subscribe('SET_HYPERPARAMS')
    async def set_hyperparams(hyperparams):
        Trainer.train_epochs = hyperparams.get("train_epochs", config.default_train_epochs)
        Trainer.train_batches = hyperparams.get("train_batches", config.default_train_batches)
        Trainer.learning_rate = hyperparams.get("lr", config.default_lr)
        Trainer._is_initialized = True


    @staticmethod
    def load_model(model_file_path):
        model = torch.load(model_file_path)
        log(model)
        return model


    @staticmethod
    @es.subscribe('TRAIN_START_EVENT')
    async def run(model_data):
        if not Trainer._is_initialized:
            raise NotInitializedError("call set_hyperparams before run")
        Trainer.model = model_data["model"]
        Trainer.model = Trainer.load_model(model_data["model_file_path"])
        asyncio.get_running_loop().create_task(Trainer.train())

    @staticmethod
    async def train():
        for i in range(Trainer.train_epochs):
            if not Trainer._is_running:
                break
            await Trainer.train_epoch()
            await es.ainvoke("EPOCH_DONE_EVENT", i)
        await es.ainvoke("TRAINER_QUIT_EVENT", {})

    @staticmethod
    async def train_epoch():
        for i in range(Trainer.train_batches):
            if not Trainer._is_running:
                break
            with ProcessPoolExecutor() as pool:
                loop = asyncio.get_running_loop()
                train_batch = partial(Trainer.train_batch, Trainer.model)
                t1 = loop.run_in_executor(pool, train_batch)
                await t1
            await es.ainvoke("BATCH_DONE_EVENT", {"index": i})

    @staticmethod
    def train_batch(model):
        log(f"моделька ({model}) начала считать батч")
        info = sum(i for i in range(100_000_000))
        log("наконец закончила, очень устала")

    @staticmethod
    @es.subscribe('APP_QUIT_EVENT')
    async def quit_handler(event_data):
        Trainer._is_running = False
        log('TRAIN QUIT')
