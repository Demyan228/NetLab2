import asyncio
from dataclasses import dataclass, field
from time import time
from common import log
import config
from event_system import EventSystem as es, EventTypes
from concurrent.futures import ProcessPoolExecutor , ThreadPoolExecutor
from functools import partial
from components.backend.PyTorchBackend import PyTorchBackend
from components.DataSet import datasets
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
        t = time()
        for i in range(Trainer.train_epochs):
            if not Trainer._is_running:
                break
            loop = asyncio.get_running_loop()
            train_epoch = partial(Trainer.train_epoch, Trainer.model, Trainer.loss_fn, Trainer.optimizer,
                                  Trainer.dataset)
            t1 = loop.run_in_executor(ppe, train_epoch)
            await t1
            train_loss, val_loss = t1.result()
            Trainer._history.train_loss.append(train_loss)
            Trainer._history.test_loss.append(val_loss)
            await es.ainvoke(EventTypes.EPOCH_DONE, {"history": Trainer._history})
        log("train done for ", time() - t, "s")
        await es.ainvoke(EventTypes.TRAINER_QUIT)

    @staticmethod
    def _forward(model, loss_fn, optimizer, data_loader):
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
            count += 1
        return sum_loss / count if count > 0 else 0

    @staticmethod
    def train_epoch(model, loss_fn, optimizer, dataset): # ANOTHER PROCESS
        log(f'{len(dataset.train_loader()) = }')
        log(f'{len(dataset.val_loader()) = }' )
        loss_train = Trainer._forward(model, loss_fn, optimizer, dataset.train_loader())
        loss_val = Trainer._forward(model, loss_fn, optimizer, dataset.val_loader())
        return loss_train , loss_val

    @staticmethod
    @es.subscribe(EventTypes.SET_DATASET_PARAMS)
    async def set_dataset_params(dataset_data):
        Trainer.dataset = datasets.get_dataset(dataset_data)
        Trainer._is_dataset_initialized = True

    @staticmethod
    @es.subscribe(EventTypes.APP_QUIT)
    async def quit_handler(event_data):
        Trainer._is_running = False
        log('TRAIN QUIT')

