import asyncio
from dataclasses import dataclass, field
from time import time
from common import log
import config
from event_system import EventSystem as es, EventTypes
from concurrent.futures import ProcessPoolExecutor , ThreadPoolExecutor
from functools import partial
from components.backend.PyTorchBackend import PyTorchBackend
from components.DataSet.CSV_Dataset import CSV_Dataset
from torch.utils.data import DataLoader


class NotInitializedError(Exception): ...
ppe = ProcessPoolExecutor()


@dataclass
class History:
    train_loss: list[float] = field(default_factory=list)
    test_loss: list[float] = field(default_factory=list)
    train_acc: float = 0
    test_acc: float = 0


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
    _history = History()

    @staticmethod
    @es.subscribe(EventTypes.SET_HYPERPARAMS)
    async def set_hyperparams(hyperparams):
        Trainer.train_epochs = hyperparams.get("num_epochs", config.default_train_epochs)
        Trainer.learning_rate = hyperparams.get("lr", config.default_lr)
        Trainer.optimizer_type = PyTorchBackend.get_optimizer(hyperparams.get("optimizer", config.default_optimizer))
        Trainer.loss_fn = PyTorchBackend.get_criterian(hyperparams.get("criterian", config.default_criterian))
        Trainer._is_hyperparams_initialized = True

    @staticmethod
    @es.subscribe(EventTypes.TRAIN_START)
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
        for _ in range(Trainer.train_epochs):
            if not Trainer._is_running:
                break
            await Trainer.train_epoch()
        await es.ainvoke(EventTypes.TRAINER_QUIT)

    @staticmethod
    def train_epoch(model, loss_fn, optimizer, data_loader):
        sum_loss = 0
        count = 0
        sum_data_means = 0
        for batch in data_loader:
            if not Trainer._is_running:
                break
            batch_loss = PyTorchBackend.train_batch(model, batch, loss_fn, optimizer)
            _, y = batch
            sum_data_means += sum(y) / len(y)
            sum_loss += batch_loss
            await es.ainvoke(EventTypes.BATCH_DONE, {"batch_loss": batch_loss})
            count += 1
        Trainer._history.train_loss.append(sum_loss / count)
        await es.ainvoke(EventTypes.EPOCH_DONE, Trainer._history)

    @staticmethod
    @es.subscribe(EventTypes.SET_DATASET_PARAMS)
    async def set_dataset_params(dataset_data):
        dataset = CSV_Dataset(dataset_data["path"], dataset_data["target_column"])
        Trainer.data_loader = DataLoader(dataset, batch_size=8, shuffle=True)
        Trainer._is_dataset_initialized = True


    @staticmethod
    @es.subscribe(EventTypes.APP_QUIT)
    async def quit_handler(event_data):
        Trainer._is_running = False
        log('TRAIN QUIT')
