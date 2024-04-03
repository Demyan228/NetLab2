import dearpygui.dearpygui as d
import config as main_config
import components.Gui.config as gui_config
import components.Gui.callbacks as cb
from components.Gui.tags import Tags
from components.Gui.nodes import NODES




def load_constructor_workspace():
    with d.file_dialog(
            tag='FILEDIALOG', 
            directory_selector=False, 
            show=False,
            callback=cb.load_file_callback, 
            width=main_config.DW // 2, 
            height=main_config.DH // 2, 
            default_path=main_config.default_dataset_path,
            ):
        d.add_file_extension('.*')
        d.add_file_extension('', color=(200, 200, 255, 255))
        d.add_file_extension('.csv', color=(200, 255, 200, 255))

    with d.group(horizontal=True, parent=Tags.CONSTRUCTOR):
        with d.child_window(tag="WindowNodeEditor", width=int(main_config.DW / 1.5)):
            with d.node_editor(
                    tag="NE", 
                    callback=cb.link_callback, 
                    delink_callback=cb.delink_callback,
                    minimap_location=d.mvNodeMiniMap_Location_BottomRight,
            ):
                pass


        with d.group():
            with d.child_window(tag='WindowHyperparams', height=int(main_config.DH / 3.5)):
                window_width = int(main_config.DW - main_config.DW / 1.5)
                label_indent = window_width // 3
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                d.add_text('Hyperparams', tag='HyperparamsTextLabel', indent=label_indent)
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                d.add_input_float(tag='HyperparamsLearningRate', label=' LearningRate', width=main_config.DW // 10, indent=gui_config.INDENT,
                                  min_value=0.000001, default_value=0.01, step=0)
                d.add_input_int(tag='HyperparamsBatchSize', label=' BatchSize', width=main_config.DW // 10, indent=gui_config.INDENT, min_value=1,
                                default_value=64, step=16, step_fast=2)
                d.add_slider_int(tag='HyperparamsNumEpochs', label=' Num Epochs', width=main_config.DW // 10, indent=gui_config.INDENT, min_value=1,
                                 default_value=10, max_value=100)
                d.add_combo(tag='HyperparamsOptimizer', label=' Optimizer', width=main_config.DW // 10, indent=gui_config.INDENT, items=['Adam', 'SDG'],
                            default_value=main_config.default_optimizer, callback=cb.debug_callback)
                d.add_combo(tag='HyperparamsCriterian', label=' Loss', width=main_config.DW // 10, indent=gui_config.INDENT,
                            items=['MSE', "MAE", 'RMSE', 'BCE', 'CCE'], default_value='MAE')
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                d.add_separator()
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                d.add_text('DataSet', tag='DatasetLabel', indent=label_indent)
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                with d.group(horizontal=True):
                    d.add_button(
                            tag='DatasetLoadButton', 
                            label='Load', 
                            callback=cb.choice_dataset_callback, 
                            width=gui_config.HYPERPARAMS_BUTTON_WIDTH, 
                            indent=gui_config.INDENT
                             )
                    d.add_button(
                            tag='DatasetCreateButton', 
                            label='Create', 
                            callback=cb.choice_dataset_callback, 
                            width=gui_config.HYPERPARAMS_BUTTON_WIDTH, 
                            indent=gui_config.INDENT + gui_config.HYPERPARAMS_BUTTON_WIDTH + gui_config.PADDING_BUTTONS_HYPERPARAMS,
                             )
                    d.add_combo(
                            tag='TargetColumn', 
                            width=main_config.DW // 15, 
                            items=["Choose dataset"], 
                            default_value='[Target]',
                            indent=(gui_config.INDENT + gui_config.PADDING_BUTTONS_HYPERPARAMS + gui_config.HYPERPARAMS_BUTTON_WIDTH)*2,
                            )
                    d.add_button(
                            tag=Tags.START_TRAIN_BUTTON, 
                            label='Train', 
                            width=main_config.DW // 20, 
                            indent=(gui_config.INDENT + gui_config.PADDING_BUTTONS_HYPERPARAMS + gui_config.HYPERPARAMS_BUTTON_WIDTH)*3 + 100,
                            )

            with d.child_window(tag='TableWindow'):
                pass
