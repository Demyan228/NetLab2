import torch
from torch import nn

class PyTorchBackend:
    @staticmethod
    async def create_model(layers):
        model = nn.Sequential()
        for layer in layers:
            layer_name = layer["layer_name"].lower()
            layer_fun = getattr(PyTorchBackend, layer_name, "unknown_layer")
            if layer_fun == "unknown_layer":
                raise ValueError(f"в PyTorchBackend нет слоя {layer_name}")
            model.append(layer_fun(layer["IN"], layer["OUT"]))
        torch.save(model, "models\\torch_model")
        return "models\\torch_model"


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