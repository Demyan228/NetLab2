import torch
from torch import nn
import os
from common import log
from concurrent.futures import ProcessPoolExecutor
from components.backend.Layers import LayerNames, Layer
import asyncio
from functools import partial
from typing import Dict
from copy import deepcopy



def RMSE(target, prediction):
    return torch.sqrt(torch.nn.MSELoss()(target, prediction))


base_layers = {LayerNames.Input: None, LayerNames.Linear: nn.Linear, LayerNames.Softmax: nn.Softmax,
               LayerNames.Sigmoid: nn.Sigmoid,
               LayerNames.Relu: nn.ReLU}


class PyTorchBackend:
    layers: Dict[str, Layer] = {ln: Layer(base_layers[ln]) for ln in base_layers}

    @staticmethod
    def add_new_layer(layer_name, layer_fun):
        PyTorchBackend.layers[layer_name] = layer_fun

    @staticmethod
    async def create_model(layers):
        model = nn.Sequential()
        for l in layers:
            layer_name = l["layer_name"]
            layer: Layer = PyTorchBackend.layers[layer_name]
            layer_params: Dict[str] = deepcopy(l)
            layer_params.pop("layer_name")
            model.append(layer.get_layer(layer_params))

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
                      "SGD": torch.optim.SGD
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
    def get_loss(model, batch: list[torch.tensor], loss_fn):
        X, labels = batch
        X, labels = X.float(), labels.float().unsqueeze(1)
        out = model(X)
        loss = loss_fn(out, labels)
        return loss

    @staticmethod
    def train_batch(model: nn.Module, batch: list[torch.tensor], loss_fn, optimizer: torch.optim.Optimizer):
        model.train()
        loss = PyTorchBackend.get_loss(model, batch, loss_fn)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        return loss.item()

    @staticmethod
    def test_batch(model: nn.Module, batch: list[torch.tensor], loss_fn):
        model.eval()
        with torch.no_grad():
            loss = PyTorchBackend.get_loss(model, batch, loss_fn)
        model.train()
        return loss.item()

    @staticmethod
    def get_layer_attributes_type(layer_name: str, expanded=False):
        return PyTorchBackend.layers[layer_name].get_attributes_type(expanded=expanded)

    @staticmethod
    def get_all_layer_names():
        return PyTorchBackend.layers.keys()
