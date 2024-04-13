import inspect
from dataclasses import dataclass

class LayerNames:
    Input = "input"
    Linear = "linear"
    Relu = "relu"
    Sigmoid = "sigmoid"
    Softmax = "softmax"


@dataclass
class LayerParamsName:
    inputs: list[str]
    outputs: list[str]
    other_params: list[str]


class Layer:
    def __init__(self, fun):
        self.fun = fun

    def get_parameters_name(self, expanded=False) -> LayerParamsName:
        #TODO
        # Мега заглушка, должна быть переработана
        #pars = inspect.signature(self.fun).parameters
        #par_list = [name for name, param in pars.items() if not expanded and param.default == inspect.Parameter.empty]
        #par_list.remove("input")
        #par_list.remove("output")
        if self.fun is None:
            return LayerParamsName([], ["out_features"], [])
        return LayerParamsName(["in_features"], ["out_features"], [])


    def get_layer(self, layer_params):
        if self.fun.__name__ != "Linear":
            layer_params={}
        return self.fun(**layer_params)