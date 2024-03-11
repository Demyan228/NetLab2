import torch
from torch import nn
import os
from common import log
from concurrent.futures import ProcessPoolExecutor
import asyncio
from functools import partial

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
            log(t1.result())
            return t1.result()

    @staticmethod
    def train_batch(model):
        log(f"моделька ({model}) начала считать батч")
        info = sum(i for i in range(100_000_000))
        log("наконец закончила, очень устала")

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
