import os
from collections import defaultdict

from dearpygui import dearpygui as d

import config
from common import log
from components.Gui.nodes import NODES
from components.Gui.core import links_graph, links_elements
from components.Gui import core
import pandas as pd
import pickle

def create_csv_table(csv_file):
    df = pd.read_csv(csv_file, encoding="utf8")
    d.configure_item("TargetColumn", items=df.columns.tolist())
    if d.does_alias_exist('Table'):
        d.delete_item('Table')
    with d.tab_bar(tag='Table', parent='TableWindow'):
        with d.tab(label='Presentation'):
            with d.table(
                    tag='TablePresentation', policy=d.mvTable_SizingStretchProp,
                    borders_innerH=True, borders_outerH=False, borders_innerV=True, borders_outerV=False,
                    scrollY=False,
                    ):
                if len(df.columns) > 7:
                    columns = df.columns[0:3].tolist() + ['...'] + df.columns[-3:].tolist()
                else:
                    columns = df.columns
                for col in columns:
                    d.add_table_column(label=col)
                if df.shape[0] > 28:
                    num_rows = 28
                else:
                    num_rows = df.shape[0]
                num_columns = len(columns)
                for y in range(num_rows):
                    with d.table_row():
                        for x in range(num_columns):
                            if x <= num_columns // 2:
                                ix = x
                            else:
                                ix = df.shape[1] - 7 + x
                            if y <= num_rows // 2:
                                iy = y
                            else:
                                iy = df.shape[0] - 28 + y
                            if x == 3 or y == 13:
                                d.add_text('...')
                            else:
                                value = df.iloc[iy, ix]
                                d.add_text(str(value))
        with d.tab(label='Full'):
            with d.table(
                    tag='TableFull', resizable=True, policy=d.mvTable_SizingFixedSame,
                    borders_innerH=True, borders_outerH=False, borders_innerV=True, borders_outerV=False,
                    scrollX=True,
                    ):
                for col in df.columns:
                    d.add_table_column(label=col)
                for y in range(df.shape[0]):
                    with d.table_row():
                        for x in range(df.shape[1]):
                            d.add_text(str(df.iloc[y, x]))


def choice_dataset_callback(sender, app_data):
    d.show_item('FILEDIALOG')

def load_file_callback(sender, app_data):
    file_path = list(app_data['selections'].values())[0]
    core.change_dataset_path(file_path)
    create_csv_table(file_path)

def save_model_struct_callback(sender, app_data):
    choosen_nodes = d.get_selected_nodes("WindowNodeEditor")
    if not choosen_nodes:
        choosen_nodes = [d.get_alias_id(i) for i in core.all_nodes_tags]
    choosen_nodes = set(choosen_nodes)
    nodes_conf = []
    links_graph = defaultdict(list)
    for n in choosen_nodes:
        conf = d.get_item_configuration(n)
        nodes_conf.append(conf)
        links_graph[n] = [i for i in core.links_graph[n] if i in choosen_nodes]
    struct_name = d.get_value("StructName")
    if struct_name in os.listdir(config.model_structs_path):
        i = 1
        while f"{struct_name}({i}).txt" in os.listdir(config.model_structs_path):
            i += 1
        struct_name = f"{struct_name}({i})"
    with open(f"{struct_name}.txt", "wb") as f:
        file_info = {"nodes_conf": nodes_conf, "links_graph": links_graph}
        pickle.dump(file_info, f)


def load_model_struct(sender, app_data):
    file_path = app_data["file_path"]
    with open(file_path, "rb") as f:
        obj = pickle.load(f)
        






def debug_callback(sender, app_data, user_data):
    text = f"""
    ==================================
    DEBUG CALLBACK:
     --------------------------------
            {sender = }
     --------------------------------
     """
    if isinstance(app_data, dict):
        text += '       app_data =\n'
        for key, value in app_data.items():
            text += f'      {key} : {value}\n'
    else:
        text += f'      {app_data = }'
    text += f"""
     --------------------------------
            {user_data = }
     --------------------------------
    ==================================
    """
    log(text)


def in_out_source_callback(input_attr: str, source):
    out_id = input_attr.replace("IN", "OUT")
    d.set_item_source(out_id, source)


def delink_callback(_, app_data):
    left, right = links_elements[app_data]
    links_graph[left].remove(right)
    d.delete_item(app_data)
    del links_elements[app_data]


def link_callback(sender, app_data):
    left, right = app_data
    links_graph[left].append(right)
    link = d.add_node_link(left, right, parent=sender)
    links_elements[link] = (left, right)
    left_output = d.get_item_alias(d.get_item_children(left)[1][0])
    right_input = d.get_item_alias(d.get_item_children(right)[1][0])
    d.set_item_source(right_input, left_output)
    for func in ['RELU', 'SIGMOID', 'SOFTMAX']:
        if func in right_input:
            in_out_source_callback(right_input, left_output)


def ne_popup_callback(_):
    pos = d.get_mouse_pos(local=False)
    if d.does_item_exist("NEPOPUP"):
        d.set_item_pos("NEPOPUP", pos=pos)
        d.show_item("NEPOPUP")
    else:
        with d.window(
            tag="NEPOPUP",
            pos=pos,
            no_title_bar=True,
            no_resize=True,
            no_move=True,
            popup=True,
        ):
            for node_type, callback in NODES.items():
                if node_type == "sep":
                    d.add_spacer(height=1)
                    d.add_separator()
                    d.add_spacer(height=1)
                else:
                    d.add_button(label=node_type, callback=callback, width=200)

def visible_map_callback(sender, app_data):
    minimap_visible = d.get_item_configuration("NE")["minimap"]
    d.configure_item("NE", minimap=not minimap_visible)