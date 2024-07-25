import asyncio
import os
from collections import defaultdict
from time import time

from dearpygui import dearpygui as d

from common import log
from event_system import EventSystem as es, EventTypes
import config as main_config
import components.Gui.config as gui_config
from components.Gui.handler_registry import init_handler_registry
from components.Gui.nodes import NodeMaster
from components.Gui import core
from components.Gui.tags import Tags
from components.Gui.test_configuration import init as test_init

from components.Gui.workspace_window.data_analysis_workspace_window import load_data_analysis_workspace
from components.Gui.workspace_window.ensemble_workspace_window import load_ensemble_workspace
from components.Gui.workspace_window.constructor_workspace_window import load_constructor_workspace
from components.Gui.workspace_window.train_workspace_window import load_train_workspace


def _dpg_pre_init():
    d.create_context()
    with d.font_registry():
        font = d.add_font(main_config.MAIN_FONT, main_config.MAIN_FONT_SIZE)
        d.bind_font(font)
    d.create_viewport(width=main_config.DW, height=main_config.DH, title='Net Lab', x_pos=0, y_pos=0)


def _dpg_post_init():
    init_handler_registry()
    d.set_primary_window(Tags.PRIMARY_WINDOW, True)
    d.setup_dearpygui()
    d.show_viewport()
#     test_init()


class PrimaryWindow:

    def __init__(self):
        self._current_ws_tag = Tags.WW_CONSTRUCTOR
        with d.window(tag=Tags.PRIMARY_WINDOW):
            with d.child_window(tag=Tags.SWITCH_PANEL_WINDOW, height=60):
                with d.group(horizontal=True):
                    workspaces_count = 4 # TODO: need procedure
                    d.add_text('', indent=(main_config.DW // 2 - (workspaces_count * gui_config.SWITCH_PANEL_BUTTON_WIDTH) // 2))
                    d.add_button(
                            label='CONSTRUCTOR', 
                            width=gui_config.SWITCH_PANEL_BUTTON_WIDTH, 
                            callback=lambda: self.change_workspace_window(Tags.WW_CONSTRUCTOR)
                            )
                    d.add_button(
                            label='ENSEMBLE', 
                            width=gui_config.SWITCH_PANEL_BUTTON_WIDTH, 
                            callback=lambda: self.change_workspace_window(Tags.WW_ENSEMBLE)
                            )
                    d.add_button(
                            label='DATA ANALYSIS', 
                            width=gui_config.SWITCH_PANEL_BUTTON_WIDTH, 
                            callback=lambda: self.change_workspace_window(Tags.WW_DATA_ANALYSIS)
                            )
                    d.add_button(
                            label='TRAIN', 
                            width=gui_config.SWITCH_PANEL_BUTTON_WIDTH, 
                            callback=lambda: self.change_workspace_window(Tags.WW_TRAIN)
                            )
            with d.child_window(tag=Tags.WW_CONSTRUCTOR):
                load_constructor_workspace()

            with d.child_window(tag=Tags.WW_ENSEMBLE):
                load_ensemble_workspace()
            d.hide_item(Tags.WW_ENSEMBLE)
            with d.child_window(tag=Tags.WW_DATA_ANALYSIS):
                load_data_analysis_workspace()
            d.hide_item(Tags.WW_DATA_ANALYSIS)
            with d.child_window(tag=Tags.WW_TRAIN):
                load_train_workspace()
            d.hide_item(Tags.WW_TRAIN)

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
        NodeMaster.load_nodes_struct(os.path.join(main_config.model_structs_path, gui_config.autosave_filename))

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
        if not NodeMaster.get_start_node():
            log("warning vse ploxo")
            return []
        links_graph = defaultdict(list)
        for inp_node in NodeMaster.nodes_graph:
            res = []
            for out_node in NodeMaster.nodes_graph[inp_node]:
                res.append(NodeMaster.get_input(out_node))
            links_graph[NodeMaster.get_output(inp_node)] = res
        layers = []
        cur_attr = d.get_item_children(d.get_alias_id(NodeMaster.get_start_node()))[1][-1]
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
        target_column = d.get_value(Tags.DATASET_TARGET_COLUMN)
        criterian = d.get_value("HyperparamsCriterian")
        optimizer = d.get_value("HyperparamsOptimizer")
        num_epochs = d.get_value('HyperparamsNumEpochs')
        batch_size = d.get_value('HyperparamsBatchSize')
        splits = d.get_value(Tags.SPLITS_HYPERPARAMS)[:-1]
        splits = [i / 100 for i in splits]
        es.invoke(EventTypes.SET_HYPERPARAMS, {"lr": lr, "optimizer": optimizer, "criterian": criterian, 'num_epochs': num_epochs})
        es.invoke(EventTypes.SET_DATASET_PARAMS, {"path": core.current_dataset_path, "target_column": target_column, "splits": splits, 'batch_size': batch_size})
        es.invoke(EventTypes.ASSEMBLE_MODEL, {"layers": layers})
        GUI._primary_window.change_workspace_window(Tags.WW_TRAIN)

    @staticmethod
    @es.subscribe(EventTypes.START_APP)
    async def run(_):
        GUI.init()
        loop = asyncio.get_running_loop()
        loop.create_task(GUI.update())

    @staticmethod
    @es.subscribe(EventTypes.APP_QUIT)
    async def quit_handler(_):
        GUI._is_running = False
        NodeMaster.save_full_struct(gui_config.autosave_filename, replace=True)
        d.destroy_context()
        log('GUI QUIT')
