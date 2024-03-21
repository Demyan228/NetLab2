import asyncio
from time import time
from common import log
import config
from event_system import EventSystem as es
from dearpygui import dearpygui as dpg
from components.Gui.core import links_graph
import os
from components.Gui import core
from components.Gui.callbacks import create_csv_table

class GUI:
    _is_running = True
    _last_render_time = time()
    max_delay = 1 / config.FPS
    model_params = None
    is_train_start = False

    @staticmethod
    def init():
        from components.Gui import verstka
        verstka.init()
        dpg.set_item_callback("train", GUI.assemble_callback)
        core.change_dataset_path(os.path.join(config.default_dataset_path, config.TEST_DATASET))
        create_csv_table(os.path.join(config.default_dataset_path, config.TEST_DATASET))

    @staticmethod
    async def _delay():
        delta = time() - GUI._last_render_time
        delay = max(0, GUI.max_delay - delta)
        await asyncio.sleep(delay)
        GUI._last_render_time = time()

    @staticmethod
    async def update():
        dpg.show_viewport()
        while dpg.is_dearpygui_running():
            await GUI._delay()
            dpg.render_dearpygui_frame()
        es.invoke("APP_QUIT_EVENT", {})

    @staticmethod
    def get_model_layers():
        if not dpg.does_item_exist("start_node"):
            log("warning vse ploxo")
            return []
        layers = []
        cur_attr = dpg.get_alias_id("start_node")
        while len(links_graph[dpg.get_item_children(dpg.get_item_parent(cur_attr))[1][-1]]) != 0:
            par = dpg.get_item_parent(cur_attr)
            cur_attr = links_graph[dpg.get_item_children(par)[1][-1]][0]
            layer = {}
            inp_attr = cur_attr
            node = dpg.get_item_parent(inp_attr)
            children = dpg.get_item_children(node)[1]
            layer["layer_name"] = dpg.get_item_label(node)
            for c in children:
                c = dpg.get_item_children(c)[1][0]
                layer[dpg.get_item_alias(c).split("-")[-1]] = dpg.get_value(c)
            layers.append(layer)
        return layers

    @staticmethod
    def assemble_callback():
        lr = dpg.get_value("HyperparamsLearningRate")
        layers = GUI.get_model_layers()
        target_column = dpg.get_value("TargetColumn")
        criterian = dpg.get_value("HyperparamsCriterian")
        optimizer = dpg.get_value("HyperparamsOptimizer")
        es.invoke("SET_HYPERPARAMS", {"lr": lr, "optimizer": optimizer, "criterian": criterian})
        es.invoke("SET_DATASET_PARAMS", {"path": core.current_dataset_path, "target_column": target_column})
        es.invoke("ASSEMBLE_MODEL_EVENT", {"layers": layers})

    @staticmethod
    @es.subscribe('APP_START_EVENT')
    async def run(_):
        GUI.init()
        loop = asyncio.get_running_loop()
        loop.create_task(GUI.update())

    @staticmethod
    @es.subscribe('EPOCH_DONE_EVENT')
    async def print_epoch_info(info):
        log(f'[{info["loss"]} EPOCH Loss]')

    @staticmethod
    @es.subscribe('APP_QUIT_EVENT')
    async def quit_handler(event_data):
        GUI._is_running = False
        dpg.destroy_context()
        log('GUI QUIT')
