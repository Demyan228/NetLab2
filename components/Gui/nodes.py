import dearpygui.dearpygui as d
from itertools import count
from functools import partial
from config import DW, DH
from components.Gui import core


class UUID:
    __generator = None

    @staticmethod
    def __node_uuid_generator():
        for idx in count(1):
            yield idx

    @staticmethod
    def get_node_uuid():
        if UUID.__generator is None:
            UUID.__generator = UUID.__node_uuid_generator()
        return next(UUID.__generator)


BIAS_X = -DW // 40
BIAS_Y = -DW// 40
NODE_WIDTH = DW // 20


def node(node_handler):
    def inner(*args, **kwargs):
        x, y = d.get_mouse_pos(local=False)
        pos = x + BIAS_X, y + BIAS_Y
        node_handler(pos=pos, parent="NE", *args, **kwargs)
        d.hide_item("NEPOPUP")
    return inner


def input_node():
    return d.node_attribute(attribute_type=d.mvNode_Attr_Input)


def output_node(tag: int|str=0):
    return d.node_attribute(attribute_type=d.mvNode_Attr_Output, tag=tag)

Node = partial(d.node, parent='NE')

@node
def node_sigmoid(parent, pos):
    in_tag, out_tag = get_in_out_tags('SIGMOID')
    with Node(label='Sigmoid', pos=pos):
        with d.node_attribute(attribute_type=d.mvNode_Attr_Input):
            d.add_input_int(tag=in_tag, step=0, width=NODE_WIDTH)
        with d.node_attribute(attribute_type=d.mvNode_Attr_Output):
            d.add_input_int(tag=out_tag, step=0, width=NODE_WIDTH)


@node
def node_softmax(parent, pos):
    in_tag, out_tag = get_in_out_tags('SOFTMAX')
    with d.node(label='Softmax', pos=pos, parent=parent):
        with input_node():
            d.add_input_int(tag=in_tag, step=0, width=NODE_WIDTH)
        with output_node():
            d.add_input_int(tag=out_tag, step=0, width=NODE_WIDTH)

@node
def node_input(parent, pos):
    if d.does_item_exist("start_node"):
        return
    _, out_tag = get_in_out_tags("INPUT")
    with d.node(label="Input", pos=pos, parent=parent):
        with output_node("start_node"):
            d.add_input_int(tag=out_tag, step=0, width=NODE_WIDTH)


@node
def node_linear_layers(parent, pos):
    in_tag, out_tag = get_in_out_tags("LINEAR")
    with d.node(label="Linear", pos=pos, parent=parent):
        with input_node():
            d.add_input_int(tag=in_tag, step=0, width=NODE_WIDTH)
        with output_node():
            d.add_input_int(tag=out_tag, step=0, width=NODE_WIDTH)


@node
def node_relu(parent, pos):
    in_tag, out_tag = get_in_out_tags("RELU")
    with d.node(label="Relu", pos=pos, parent=parent):
        with input_node():
            d.add_input_int(tag=in_tag, step=0, width=NODE_WIDTH)
        with output_node():
            d.add_input_int(tag=out_tag, step=0, width=NODE_WIDTH)


def get_in_out_tags(node_type: str):
    uuid = UUID.get_node_uuid()
    in_tag = f"{node_type}-{uuid}-IN"
    out_tag = f"{node_type}-{uuid}-OUT"
    return in_tag, out_tag


NODES = {
    "input": node_input,
    "linear": node_linear_layers,
    "sep": None,
    "relu": node_relu,
    "sigmoid": node_sigmoid,
    "softmax": node_softmax,
}
