import os
from collections import defaultdict

from dearpygui import dearpygui as d
from pandas.core.dtypes.dtypes import np

from components.Gui.tags import Tags
from common import log
import config
from common import log
from components.Gui.nodes import NodeMaster
from components.Gui import core
from components.Gui.config import BIAS_X, BIAS_Y
from config import DW, DH
from components.backend.PyTorchBackend import PyTorchBackend as Backend
import pandas as pd
import pickle


def create_csv_table(csv_file):
    df = pd.read_csv(csv_file, encoding="utf8")
    d.configure_item(Tags.DATASET_TARGET_COLUMN, items=df.columns.tolist())
    if d.does_alias_exist(Tags.DATASET_TABLE):
        d.delete_item(Tags.DATASET_TABLE)
    with d.table(
            tag=Tags.DATASET_TABLE, 
            resizable=True, 
            policy=d.mvTable_SizingFixedSame,
            borders_innerH=True, 
            borders_outerH=False, 
            borders_innerV=True, 
            borders_outerV=False,
            scrollX=True,
            parent=Tags.TABLE_PRESENTATION_WINDOW,
            ):
        for col in df.columns:
            d.add_table_column(label=col)
        for y in range(df.shape[0]):
            with d.table_row():
                for x in range(df.shape[1]):
                    value = df.iloc[y, x]
                    if type(value) == np.float64:
                        value = round(value, 3)
                    d.add_text(str(value))


def choice_dataset_callback(sender, app_data, user_data):
    d.show_item('FILEDIALOG')
    d.configure_item('FILEDIALOG', directory_selector=user_data)

def load_file_callback(sender, app_data):
    log(list(app_data['selections'].values()))
    file_path = list(app_data['selections'].values())[0]
    core.change_dataset_path(file_path)
#     create_csv_table(file_path) # TODO: show_dataset_info

def save_model_struct_callback(sender, app_data):
    struct_name = d.get_value("model_struct_name")
    NodeMaster.save_struct(struct_name)
    d.delete_item("save_struct_menu")


def open_save_struct_menu_callback(sender, app_data):
    if d.does_item_exist("save_struct_menu"):
        d.show_item("save_struct_menu")
    else:
        with d.window(label="Save model", tag="save_struct_menu", pos=(DW // 2, DH // 2), width=300, height=180):
            d.add_input_text(id="model_struct_name", hint="struct name", width=300)
            d.add_button(label="Save", callback=save_model_struct_callback, indent=100)


def delete_key_pressed_callback(sender, app_data):
    if d.does_item_exist("NE"):
        NodeMaster.delete_selected()


def open_load_struct_menu_callback(sender, app_data):
    d.show_item("STRUCT_FILEDIALOG")

def load_model_struct_callback(sender, app_data):
    file_path = list(app_data['selections'].values())[0]
    NodeMaster.load_nodes_struct(file_path)

        
def user_create_node(sender, app_data, layer_name):
    pos = d.get_item_pos("NEPOPUP")
    pos = pos[0] + BIAS_X, pos[1] + BIAS_Y
    NodeMaster.create_default_node(layer_name, pos)
    d.hide_item("NEPOPUP")


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


def delink_callback(_, app_data):
    NodeMaster.delete_link(app_data)


def link_callback(sender, app_data):
    left, right = app_data
    NodeMaster.create_link(left, right, sender=sender)


def show_node_menu_callback(_):
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
            for node_type in Backend.get_all_layer_names():
                d.add_button(label=node_type, callback=user_create_node, user_data=node_type, width=200)
            d.add_spacer()
            d.add_separator()
            d.add_spacer()
            d.add_button(label="save", callback=open_save_struct_menu_callback, width=200)
            d.add_button(label="load", callback=open_load_struct_menu_callback, width=200)

def visible_map_callback(sender, app_data):
    minimap_visible = d.get_item_configuration("NE")["minimap"]
    d.configure_item("NE", minimap=not minimap_visible)
