import asyncio
from time import time
from common import log
import config
from event_system import EventSystem as es
from concurrent.futures import ProcessPoolExecutor , ThreadPoolExecutor
from functools import partial
from components.backend.PyTorchBackend import PyTorchBackend
from components.DataSet.CSV_Dataset import CSV_Dataset
from torch.utils.data import DataLoader
import torch

ppe = ProcessPoolExecutor()


class NotInitializedError(Exception): ...

class Trainer:
    _last_render_time = time()
    _is_running = True
    train_epochs: int = 0
    learning_rate: int = 0
    optimizer_type = None
    optimizer = None
    data_loader: DataLoader = None
    loss_fn = None
    model = None
    _is_hyperparams_initialized = False
    _is_dataset_initialized = False

    @staticmethod
    @es.subscribe('SET_HYPERPARAMS')
    async def set_hyperparams(hyperparams):
        Trainer.train_epochs = hyperparams.get("train_epochs", config.default_train_epochs)
        Trainer.learning_rate = hyperparams.get("lr", config.default_lr)
        Trainer.optimizer_type = PyTorchBackend.get_optimizer(hyperparams.get("optimizer", config.default_optimizer))
        Trainer.loss_fn = PyTorchBackend.get_criterian(hyperparams.get("criterian", config.default_criterian))
        Trainer._is_hyperparams_initialized = True

    @staticmethod
    @es.subscribe('TRAIN_START_EVENT')
    async def run(model_data):
        if not Trainer._is_hyperparams_initialized:
            raise NotInitializedError("  all set_hyperparams before run")
        if not Trainer._is_dataset_initialized:
            raise NotInitializedError("  dataset info not initialized before run")
        Trainer.model = await PyTorchBackend.load_model(model_data["model_file_path"])
        Trainer.optimizer = Trainer.optimizer_type(Trainer.model.parameters(), Trainer.learning_rate)
        asyncio.get_running_loop().create_task(Trainer.train())


    @staticmethod
    async def train():
        for i in range(Trainer.train_epochs):
            if not Trainer._is_running:
                break
            await Trainer.train_epoch()
        await es.ainvoke("TRAINER_QUIT_EVENT", {})

    @staticmethod
    async def train_epoch():
        sum_loss = 0
        count = 0
        for batch in Trainer.data_loader:
            if not Trainer._is_running:
                break
            loop = asyncio.get_running_loop()
            train_batch = partial(PyTorchBackend.train_batch, Trainer.model, batch, Trainer.loss_fn, Trainer.optimizer)
            t1 = loop.run_in_executor(ppe, train_batch)
            await t1
            batch_loss = t1.result()
            sum_loss += batch_loss
            await es.ainvoke("BATCH_DONE_EVENT", {"batch_loss": batch_loss})
            count += 1
        await es.ainvoke("EPOCH_DONE_EVENT", {"loss": sum_loss / count})

    @staticmethod
    @es.subscribe('SET_DATASET_PARAMS')
    async def set_dataset_params(dataset_data):
        dataset = CSV_Dataset(dataset_data["path"], dataset_data["target_column"])
        Trainer.data_loader = DataLoader(dataset, batch_size=8, shuffle=True)
        Trainer._is_dataset_initialized = True



    @staticmethod
    @es.subscribe('APP_QUIT_EVENT')
    async def quit_handler(event_data):
        Trainer._is_running = False
        log('TRAIN QUIT')
