import inspect
from dataclasses import dataclass

class LayerNames:
    Input = "input"
    Linear = "linear"
    Relu = "relu"
    Sigmoid = "sigmoid"
    Softmax = "softmax"

class AttributesType:
    input = "input"
    output = "output"
    int = "int"
    string = "string"


@dataclass
class LayerAttributesType:
    params_type: dict[str, str]



class Layer:
    def __init__(self, fun):
        self.fun = fun

    def get_attributes_type(self, expanded=False) -> LayerAttributesType:
        #TODO
        # Мега заглушка, должна быть переработана
        # Чтоб ее переработать надо изменить в gui цеплялки нод(ну типо у релу нет параметров и инпута, но приценить стрелочку как то наддо
        #pars = inspect.signature(self.fun).parameters
        #par_list = [name for name, param in pars.items() if not expanded and param.default == inspect.Parameter.empty]
        #par_list.remove("input")
        #par_list.remove("output")
        if self.fun is None:
            return LayerAttributesType({"out_features": AttributesType.output})
        return LayerAttributesType({"in_features": AttributesType.input, "out_features": AttributesType.output})


    def get_layer(self, layer_params):
        if self.fun.__name__ != "Linear":
            layer_params={}
        return self.fun(**layer_params)