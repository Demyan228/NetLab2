from collections import defaultdict
from dataclasses import dataclass
import dearpygui.dearpygui as d
from itertools import count
import config
import os
import pickle

from common import log
from components.Gui.config import NODE_PARAM_WIDTH
from components.backend.Layers import LayerNames
from components.backend.Layers import LayerAttributesType, AttributesType
from components.backend.PyTorchBackend import PyTorchBackend as Backend



nodes_count= defaultdict(int)
def get_node_tag(node_type):
    nodes_count[node_type] += 1
    tag = f"{node_type}{nodes_count[node_type]}"
    return tag

def create_input_node(*args, **kwargs):
    with d.node_attribute(attribute_type=d.mvNode_Attr_Input):
        d.add_input_int(*args, **kwargs)

def create_output_node(*args, **kwargs):
    with d.node_attribute(attribute_type=d.mvNode_Attr_Output):
        d.add_input_int(*args, **kwargs)


@dataclass
class LayerConfiguration:
    layer_name: str
    pos: tuple[int, int]
    attributes: dict[str, dict]


dict_attributes_dpgtype = {AttributesType.input: create_input_node, AttributesType.output: create_output_node, AttributesType.int: d.add_input_int}

class NodeMaster:
    nodes_graph = defaultdict(list) # node_id: list(node_ids)
    links_elements = {}     # link_id: (node_id1, node_id2
    node_links = defaultdict(list)     # node_id: list(link_ids)
    all_nodes_baseconf: dict[str: LayerConfiguration] = {}   # tag: LayerConfiguration, для разнообразия тэг вместо id )



    @staticmethod
    def create_default_node(layer_name, pos):
        names: LayerAttributesType = Backend.get_layer_attributes_type(layer_name)
        attributes = {}
        for name, t in names.params_type.items():
            attributes[name] = {"type": t, "default_value": 0}
        layer_params = LayerConfiguration(layer_name, pos, attributes)
        return NodeMaster.create_node(layer_params)

    @staticmethod
    def create_node(configuration: LayerConfiguration):
        layer_name = configuration.layer_name
        tag = get_node_tag(layer_name)
        NodeMaster.all_nodes_baseconf[tag] = configuration
        with d.node(label=layer_name, pos=configuration.pos, tag=tag, parent="NE"):
            for attribute_name, attr_params in configuration.attributes.items():
                dict_attributes_dpgtype[attr_params["type"]](tag=tag + "-" + attribute_name, step=0, width=NODE_PARAM_WIDTH,
                                                             default_value=attr_params["default_value"])
        return tag
    @staticmethod
    def create_nodes(configurations: list[LayerConfiguration]):
        res= []
        for configuration in configurations:
            res.append(NodeMaster.create_node(configuration))
        return res

    @staticmethod
    def create_link(left, right, sender="NE"):
        left_node = d.get_item_parent(left)
        right_node = d.get_item_parent(right)
        NodeMaster.nodes_graph[left_node].append(right_node)
        link = d.add_node_link(left, right, parent=sender)
        NodeMaster.links_elements[link] = (left_node, right_node)
        NodeMaster.node_links[left_node].append(link)
        NodeMaster.node_links[right_node].append(link)
        left_output = d.get_item_alias(d.get_item_children(left)[1][0])
        right_input = d.get_item_alias(d.get_item_children(right)[1][0])
        d.set_item_source(right_input, left_output)
        for func in [LayerNames.Relu, LayerNames.Sigmoid, LayerNames.Softmax]:
            if func in right_input:
                out_id = right_input.replace("in_features", "out_features")
                d.set_item_source(out_id, left_output)
        return link

    @staticmethod
    def delete_link(link_id):
        left_node, right_node = NodeMaster.links_elements[link_id]
        NodeMaster.nodes_graph[left_node].remove(right_node)
        NodeMaster.node_links[left_node].remove(link_id)
        NodeMaster.node_links[right_node].remove(link_id)
        d.delete_item(link_id)
        del NodeMaster.links_elements[link_id]
    @staticmethod
    def delete_selected():
        selected_nodes = d.get_selected_nodes("NE")
        for link in d.get_selected_links("NE"):
            NodeMaster.delete_link(link)
        for node in selected_nodes:
            NodeMaster.delete_node(node)

    @staticmethod
    def get_start_node():
        for tag, conf in NodeMaster.all_nodes_baseconf.items():
            if conf.layer_name == LayerNames.Input:
                return tag
        return False

    @staticmethod
    def delete_node(node_id):
        need_to_delete_links = NodeMaster.node_links[node_id] * 1
        for link_id in need_to_delete_links:
            NodeMaster.delete_link(link_id)
        if node_id in NodeMaster.nodes_graph: del NodeMaster.nodes_graph[node_id]
        if node_id in NodeMaster.node_links: del NodeMaster.node_links[node_id]
        del NodeMaster.all_nodes_baseconf[d.get_item_alias(node_id)]
        d.delete_item(node_id)



    @staticmethod
    def create_links(links, sender="NE"):
        link_ids = []
        for params in links:
            link_ids.append(NodeMaster.create_link(*params, sender=sender))
        return link_ids

    @staticmethod
    def get_node_configuration(tag) -> LayerConfiguration:
        base_conf: LayerConfiguration = NodeMaster.all_nodes_baseconf[tag]
        layer_name = base_conf.layer_name
        x, y = d.get_item_pos(tag)
        pos = (x, y)
        attributes = {}
        for ch in d.get_item_children(tag)[1]:
            attr = d.get_item_alias(d.get_item_children(ch)[1][0])
            attr_name = attr.split("-")[1]
            type = base_conf.attributes[attr_name]["type"]
            attributes[attr_name] = {"type": type, "default_value": d.get_value(attr)}
        return LayerConfiguration(layer_name, pos, attributes)

    @staticmethod
    def _save_nodes_struct(struct_name, nodes_tags, replace):
        nodes_tags = set(nodes_tags)
        nodes_id = set([d.get_alias_id(tag) for tag in nodes_tags])
        nodes_conf = {}
        links = []
        for n in nodes_tags:
            node_id = d.get_alias_id(n)
            conf = NodeMaster.get_node_configuration(n)
            nodes_conf[node_id] = conf
            links.extend([[node_id, i] for i in NodeMaster.nodes_graph[node_id] if i in nodes_id])
        if not replace and struct_name in os.listdir(config.model_structs_path):
            i = 1
            while f"{struct_name}({i})" in os.listdir(config.model_structs_path):
                i += 1
            struct_name = f"{struct_name}({i})"
        struct_path = os.path.join(config.model_structs_path, struct_name)
        with open(f"{struct_path}", "wb") as f:
            file_info = {"nodes_conf": nodes_conf, "links_graph": links}
            pickle.dump(file_info, f)


    @staticmethod
    def save_full_struct(struct_name, replace=False):
        NodeMaster._save_nodes_struct(struct_name, list(NodeMaster.all_nodes_baseconf.keys()), replace)

    @staticmethod
    def save_struct(struct_name, replace=False):
        selected_nodes = [d.get_item_label(i) for i in d.get_selected_nodes("NE")]
        if not selected_nodes:
            selected_nodes = list(NodeMaster.all_nodes_baseconf.keys())
        NodeMaster._save_nodes_struct(struct_name, selected_nodes, replace)

    @staticmethod
    def get_output(node_id):
        for i in d.get_item_children(node_id)[1]:
            if d.get_item_configuration(i)["attribute_type"] == d.mvNode_Attr_Output:
                return i

    @staticmethod
    def get_input(node_id):
        for i in d.get_item_children(node_id)[1]:
            if d.get_item_configuration(i)["attribute_type"] == d.mvNode_Attr_Input:
                return i


    @staticmethod
    def load_nodes_struct(file_path):
        if not os.path.exists(file_path):
            return
        with open(file_path, "rb") as f:
            obj = pickle.load(f)
            nodes_conf, links = obj["nodes_conf"], obj["links_graph"]
        new_ids = [d.get_alias_id(i) for i in NodeMaster.create_nodes(nodes_conf.values())]
        old_ids = list(nodes_conf.keys())
        old_new_ids = {old_ids[i]: new_ids[i] for i in range(len(new_ids))}
        for i in range(len(links)):
            NodeMaster.get_output(old_new_ids[links[i][0]])
            links[i][0] = NodeMaster.get_output(old_new_ids[links[i][0]])
            links[i][1] = NodeMaster.get_input(old_new_ids[links[i][1]])
        link_ids = NodeMaster.create_links(links)

