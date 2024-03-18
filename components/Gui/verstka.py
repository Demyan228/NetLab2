import dearpygui.dearpygui as d

import config
from config import DW, DH, indent, default_dataset_path
import components.Gui.callbacks as cb


d.create_context()

with d.font_registry():
    font = d.add_font("resources/font.ttf", 40)
    d.bind_font(font)

with d.file_dialog(
        tag='FILEDIALOG', directory_selector=False, show=False,
        # callback=load_file_callback, width=1920, height=1080, default_path='/home/user/datasets/',
        callback=cb.load_file_callback, width=DW / 2, height=DH / 2, default_path=default_dataset_path,
):
    d.add_file_extension('.*')
    d.add_file_extension('', color=(200, 200, 255, 255))
    d.add_file_extension('.csv', color=(200, 255, 200, 255))

with d.window(tag="WindowNodeEditor", width=DW // 1.8, height=DH - indent * 3, pos=(indent, indent), no_title_bar=True,
              no_resize=True, no_move=True):
    with d.node_editor(
            tag="NE", callback=cb.link_callback, delink_callback=cb.delink_callback,
            minimap_location=d.mvNodeMiniMap_Location_BottomRight
    ):
        pass

with d.window(tag='WindowHyperparams', width=DW - indent * 3 - DW // 1.8, height=DH // 3,
              pos=(DW // 1.8 + indent * 2, indent), no_title_bar=True, no_resize=True, no_move=True):
    d.add_text('Hyperparams', tag='HyperparamsTextLabel', pos=(DW // 6, indent // 2))
    d.add_spacer(height=indent * 2)
    d.add_input_float(tag='HyperparamsLearningRate', label=' LearningRate', width=DW // 10, indent=indent,
                      min_value=0.000001, default_value=0.01, step=0)
    d.add_input_int(tag='HyperparamsBatchSize', label=' BatchSize', width=DW // 10, indent=indent, min_value=1,
                    default_value=64, step=16, step_fast=2)
    d.add_slider_int(tag='HyperparamsNumEpochs', label=' Num Epochs', width=DW // 10, indent=indent, min_value=1,
                     default_value=10, max_value=100)
    d.add_combo(tag='HyperparamsOptimizer', label=' Optimizer', width=DW // 10, indent=indent, items=['Adam', 'SDG'],
                default_value=config.default_optimizer, callback=cb.debug_callback)
    d.add_combo(tag='HyperparamsCriterian', label=' Loss', width=DW // 10, indent=indent,
                items=['MSE', "MAE", 'RMSE', 'BCE', 'CCE'], default_value='MAE')
    d.add_spacer(height=indent // 2.5)
    d.add_separator()
    d.add_spacer(height=indent // 2.5)
    with d.group(horizontal=True):
        d.add_button(tag='DatasetButton', label='DataSet', callback=cb.choice_dataset_callback, width=DW // 20,
                     indent=indent)
        d.add_button(tag='train', label='Train', width=DW // 20, indent=indent * 2 + DW // 20)
        d.add_combo(tag='TargetColumn', label="target_column", width=DW // 15, indent=indent + DW // 5,
                    items=["Choose dataset"], default_value='charges')

with d.window(tag='TableWindow', width=DW - indent * 3 - DW // 1.8, height=DH * 2 // 3 - indent * 4,
              pos=(DW // 1.8 + indent * 2, DH // 3 + indent * 2), no_title_bar=True, no_resize=True, no_move=True):
    pass

with d.handler_registry():
    d.add_mouse_click_handler(callback=cb.ne_popup_callback, button=1)
    d.add_key_press_handler(key=d.mvKey_M, callback=cb.visible_map_callback)


def init():
    d.create_viewport(width=DW, height=DH, title='Net Lab', x_pos=0, y_pos=0)
    d.setup_dearpygui()
