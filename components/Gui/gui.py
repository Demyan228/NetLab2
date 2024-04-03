import asyncio
from time import time
from dearpygui import dearpygui as d
import os
from common import log
from components.Gui.callbacks import create_csv_table, link_callback, load_file_callback
from event_system import EventSystem as es, EventTypes
import config as main_config
import components.Gui.config as gui_config
from components.Gui.handler_registry import init_handler_registry
from components.Gui.core import links_graph
from components.Gui import core
from components.Gui.tags import Tags
from components.Gui.workspace_window.constructor_workspace_window import load_constructor_workspace
from components.Gui.workspace_window.train_workspace_window import load_train_workspace

from components.Gui.nodes import get_in_out_tags, input_node, output_node


def _dpg_pre_init():
    d.create_context()
    with d.font_registry():
        font = d.add_font(main_config.MAIN_FONT, main_config.MAIN_FONT_SIZE)
        d.bind_font(font)
    d.create_viewport(width=main_config.DW, height=main_config.DH, title='Net Lab', x_pos=0, y_pos=0)

NODE_WIDTH = main_config.DW // 20
def node_input(parent, pos):
    if d.does_item_exist("start_node"):
        return
    _, out_tag = get_in_out_tags("INPUT")
    with d.node(label="Input", pos=pos, parent=parent):
        with output_node("start_node"):
            d.add_input_int(tag=out_tag, step=0, width=NODE_WIDTH, default_value=6)


def node_linear_layers(parent, pos):
    in_tag, out_tag = get_in_out_tags("LINEAR")
    with d.node(label="Linear", pos=pos, parent=parent):
        with input_node():
            d.add_input_int(tag=in_tag, step=0, width=NODE_WIDTH)
        with output_node():
            d.add_input_int(tag=out_tag, step=0, width=NODE_WIDTH, default_value=1)

def _dpg_post_init():
    init_handler_registry()
    d.set_primary_window(Tags.PRIMARY_WINDOW, True)
    d.setup_dearpygui()
    d.show_viewport()
    ##########################################  
    node_input(parent='NE', pos=(100, 100))
    node_linear_layers(parent='NE', pos=(400, 100))
    link_callback('NE', (82, 85))
    file_path = os.path.join(main_config.default_dataset_path, main_config.TEST_DATASET)
    core.change_dataset_path(file_path)
    create_csv_table(file_path)
    d.configure_item('TargetColumn', default_value='charges')
    ##########################################  



class PrimaryWindow:

    def __init__(self):
        self._current_ws_tag = Tags.CONSTRUCTOR
        with d.window(tag=Tags.PRIMARY_WINDOW):
            with d.child_window(tag=Tags.SWITCH_PANEL_WINDOW, height=60):
                with d.group(horizontal=True):
                    d.add_text('', indent=(main_config.DW // 2 - (2 * gui_config.SWITCH_PANEL_BUTTON_WIDTH) // 2)) # FIX: 2 -> workspaces count
                    d.add_button(label='CONSTRUCTOR', width=gui_config.SWITCH_PANEL_BUTTON_WIDTH, callback=lambda: self.change_workspace_window(Tags.CONSTRUCTOR))
                    d.add_button(label='TRAIN', width=gui_config.SWITCH_PANEL_BUTTON_WIDTH, callback=lambda: self.change_workspace_window(Tags.TRAIN))
            with d.child_window(tag=Tags.CONSTRUCTOR):
                load_constructor_workspace()
            with d.child_window(tag=Tags.TRAIN):
                load_train_workspace()
            d.hide_item(Tags.TRAIN)

    def change_workspace_window(self, ws_tag: str):
        d.hide_item(self._current_ws_tag)
        self._current_ws_tag = ws_tag
        d.show_item(self._current_ws_tag)


class GUI:
    _is_running = True
    _last_render_time = time()
    _primary_window = None
    max_delay = 1 / main_config.FPS
    model_params = None
    is_train_start = False

    @staticmethod
    def init():
        _dpg_pre_init()
        GUI._primary_window = PrimaryWindow()
        _dpg_post_init()
        d.set_item_callback(Tags.START_TRAIN_BUTTON, GUI.assemble_callback)

    @staticmethod
    async def _delay():
        delta = time() - GUI._last_render_time
        delay = max(0, GUI.max_delay - delta)
        GUI._last_render_time = time()
        await asyncio.sleep(delay)

    @staticmethod
    async def update():
        while d.is_dearpygui_running():
            await GUI._delay()
            d.render_dearpygui_frame()
        es.invoke(EventTypes.APP_QUIT)

    @staticmethod
    def get_model_layers():
        if not d.does_item_exist("start_node"):
            log("warning vse ploxo")
            return []
        layers = []
        cur_attr = d.get_alias_id("start_node")
        while len(links_graph[d.get_item_children(d.get_item_parent(cur_attr))[1][-1]]) != 0:
            par = d.get_item_parent(cur_attr)
            cur_attr = links_graph[d.get_item_children(par)[1][-1]][0]
            layer = {}
            inp_attr = cur_attr
            node = d.get_item_parent(inp_attr)
            children = d.get_item_children(node)[1]
            layer["layer_name"] = d.get_item_label(node)
            for c in children:
                c = d.get_item_children(c)[1][0]
                layer[d.get_item_alias(c).split("-")[-1]] = d.get_value(c)
            layers.append(layer)
        return layers

    @staticmethod
    def assemble_callback():
        lr = d.get_value("HyperparamsLearningRate")
        layers = GUI.get_model_layers()
        target_column = d.get_value("TargetColumn")
        criterian = d.get_value("HyperparamsCriterian")
        optimizer = d.get_value("HyperparamsOptimizer")
        num_epochs = d.get_value('HyperparamsNumEpochs')
        es.invoke(EventTypes.SET_HYPERPARAMS, {"lr": lr, "optimizer": optimizer, "criterian": criterian, 'num_epochs': num_epochs})
        es.invoke(EventTypes.SET_DATASET_PARAMS, {"path": core.current_dataset_path, "target_column": target_column})
        es.invoke(EventTypes.ASSEMBLE_MODEL, {"layers": layers})

    @staticmethod
    @es.subscribe(EventTypes.START_APP)
    async def run(_):
        GUI.init()
        loop = asyncio.get_running_loop()
        loop.create_task(GUI.update())

    @staticmethod
#     @es.subscribe(EventTypes.EPOCH_DONE)
    async def print_epoch_info(history):
        log(f'[{history.train_loss = }]')

    @staticmethod
    @es.subscribe(EventTypes.APP_QUIT)
    async def quit_handler(_):
        GUI._is_running = False
        d.destroy_context()
        log('GUI QUIT')
