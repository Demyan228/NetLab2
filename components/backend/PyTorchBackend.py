import torch
from torch import nn
import os
from common import log
from concurrent.futures import ProcessPoolExecutor
import asyncio
from functools import partial

def RMSE(target, prediction):
    return torch.sqrt(torch.nn.MSELoss()(target, prediction))



class PyTorchBackend:
    @staticmethod
    async def create_model(layers):
        model = nn.Sequential()
        for layer in layers:
            layer_name = layer["layer_name"].lower()
            layer_fun = getattr(PyTorchBackend, layer_name, None)
            if layer_fun is None:
                raise ValueError(f"в PyTorchBackend нет слоя {layer_name}")
            else:
                model.append(layer_fun(layer["IN"], layer["OUT"]))

        model_path = os.path.join('models', 'torch_model')
        if not os.path.exists(model_path):
            with open(model_path, 'w'): ...
        torch.save(model, model_path)
        return model_path

    @staticmethod
    async def load_model(model_file_path):
        with ProcessPoolExecutor() as pool:
            loop = asyncio.get_running_loop()
            load_model = partial(torch.load, model_file_path)
            t1 = loop.run_in_executor(pool, load_model)
            await t1
            return t1.result()


    @staticmethod
    def get_optimizer(optimizer_name: str):
        optimizers = {"Adam": torch.optim.Adam,
                      "SGD" : torch.optim.SGD
                      }
        return optimizers[optimizer_name]

    @staticmethod
    def get_criterian(criterian_name):
        criterians = {"RMSE": RMSE,
                      "MSE": torch.nn.MSELoss(),
                      "BCE": torch.nn.BCELoss(),
                      "CCE": RMSE,
                      "MAE": torch.nn.L1Loss(),
                      }
        return criterians[criterian_name]

    @staticmethod
    def train_batch(model, batch: list[torch.tensor], loss_fn, optimizer: torch.optim.Optimizer):
        X, labels = batch
        X, labels = X.float(), labels.float().unsqueeze(1)
        out = model(X)
        loss = loss_fn(out, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        return loss.item()

    @staticmethod
    def linear(input, output):
        return nn.Linear(input, output)

    @staticmethod
    def relu(input, output):
        return nn.ReLU()

    @staticmethod
    def sigmoid(input, output):
        return nn.Sigmoid()

    @staticmethod
    def softmax(input, output):
        return nn.Softmax()
