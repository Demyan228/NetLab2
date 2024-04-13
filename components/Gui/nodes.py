from collections import defaultdict

import dearpygui.dearpygui as d
from itertools import count
from components.Gui.config import NODE_PARAM_WIDTH
from components.backend.Layers import LayerNames
from components.backend.PyTorchBackend import PyTorchBackend as Backend


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

def node_tag_generator():
    i = 0
    while True:
        i += 1
        yield i


node_tag_gen = node_tag_generator()
def get_node_tag(node_type):
    tag = f"{node_type}{next(node_tag_gen)}"
    return tag

class NodeMaster:
    all_nodes_tags = []
    links_graph = defaultdict(list)
    links_elements = {}

    @staticmethod
    def create_node(layer_name, pos):
        params = Backend.get_layer_parameters_name(layer_name)
        tag = get_node_tag(layer_name)
        NodeMaster.all_nodes_tags.append(tag)
        with d.node(label=layer_name, pos=pos, tag=tag, parent="NE"):
            for inp_name in params.inputs:
                with input_node():
                    d.add_input_int(tag=tag+"-"+inp_name, step=0, width=NODE_PARAM_WIDTH)
            for out_name in params.outputs:
                with output_node():
                    d.add_input_int(tag=tag+"-"+out_name, step=0, width=NODE_PARAM_WIDTH)
            for other_name in params.other_params:
                d.add_input_int(tag=tag+"-"+other_name, step=0, width=NODE_PARAM_WIDTH)

    @staticmethod
    def create_nodes(nodes):
        for params in nodes:
            NodeMaster.create_node(*params)

    @staticmethod
    def create_link(left, right, sender="NE"):
        NodeMaster.links_graph[left].append(right)
        link = d.add_node_link(left, right, parent=sender)
        NodeMaster.links_elements[link] = (left, right)
        left_output = d.get_item_alias(d.get_item_children(left)[1][0])
        right_input = d.get_item_alias(d.get_item_children(right)[1][0])
        d.set_item_source(right_input, left_output)
        for func in [LayerNames.Relu, LayerNames.Sigmoid, LayerNames.Softmax]:
            if func in right_input:
                out_id = right_input.replace("in_features", "out_features")
                d.set_item_source(out_id, left_output)


    @staticmethod
    def delete_link(link_id):
        left, right = NodeMaster.links_elements[link_id]
        NodeMaster.links_graph[left].remove(right)
        d.delete_item(link_id)
        del NodeMaster.links_elements[link_id]


    @staticmethod
    def create_links(links, sender="NE"):
        for params in links:
            NodeMaster.create_link(*params, sender=sender)


def input_node():
    return d.node_attribute(attribute_type=d.mvNode_Attr_Input)


def output_node(tag: int|str=0):
    return d.node_attribute(attribute_type=d.mvNode_Attr_Output, tag=tag)


