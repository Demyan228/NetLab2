import asyncio
from time import time
from dearpygui import dearpygui as d
from common import log
import config
from event_system import EventSystem as es
from components.Gui.handler_registry import init_handler_registry
from components.Gui.core import links_graph
from components.Gui import core
from components.Gui.callbacks import create_csv_table
from components.Gui.tags import WindowTag, WorkspaceWindowTag
from components.Gui.workspace_window.constructor_workspace_window import load_constructor_workspace



def _dpg_pre_init():
    d.create_context()
    with d.font_registry():
        font = d.add_font(config.MAIN_FONT, config.MAIN_FONT_SIZE)
        d.bind_font(font)
    d.create_viewport(width=config.DW, height=config.DH, title='Net Lab', x_pos=0, y_pos=0)


def _dpg_post_init():
    init_handler_registry()
    d.set_primary_window(WindowTag.PRIMARY_WINDOW, True)
    d.setup_dearpygui()
    d.show_viewport()



class PrimaryWindow:

    def __init__(self):
        self._current_ws_tag = WorkspaceWindowTag.CONSTRUCTOR
        with d.window(tag=WindowTag.PRIMARY_WINDOW):
            with d.child_window(tag=WindowTag.SWITCH_PANEL_WINDOW, height=60):
                with d.group(horizontal=True):
                    d.add_text('', indent=(config.DW // 2 - (2 * config.SWITCH_PANEL_BUTTON_WIDTH) // 2)) # FIX: 2 -> workspaces count
                    d.add_button(label='CONSTRUCTOR', width=config.SWITCH_PANEL_BUTTON_WIDTH, callback=lambda: self.change_workspace_window(WorkspaceWindowTag.CONSTRUCTOR))
                    d.add_button(label='TRAIN', width=config.SWITCH_PANEL_BUTTON_WIDTH, callback=lambda: self.change_workspace_window(WorkspaceWindowTag.TRAIN))
            with d.child_window(tag=WorkspaceWindowTag.CONSTRUCTOR):
                load_constructor_workspace()
            with d.child_window(tag=WorkspaceWindowTag.TRAIN):
                pass
            d.hide_item(WorkspaceWindowTag.TRAIN)

    def change_workspace_window(self, ws_tag: str):
        d.hide_item(self._current_ws_tag)
        self._current_ws_tag = ws_tag
        d.show_item(self._current_ws_tag)


class GUI:
    _is_running = True
    _last_render_time = time()
    _primary_window = None
    max_delay = 1 / config.FPS
    model_params = None
    is_train_start = False

    @staticmethod
    def init():
        _dpg_pre_init()
        GUI._primary_window = PrimaryWindow()
        _dpg_post_init()
        # d.set_item_callback("train", GUI.assemble_callback)

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
        es.invoke("APP_QUIT_EVENT", {})

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
        d.destroy_context()
        log('GUI QUIT')
