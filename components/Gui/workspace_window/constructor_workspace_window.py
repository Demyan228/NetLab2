import dearpygui.dearpygui as d
import config
from config import DW, DH, indent, default_dataset_path
import components.Gui.callbacks as cb
from components.Gui.tags import WorkspaceWindowTag


PADDING_BUTTONS_HYPERPARAMS = 10
BUTTON_WIDTH_HYPERPARAMS = 200


def load_constructor_workspace():
    with d.file_dialog(
            tag='FILEDIALOG', 
            directory_selector=False, 
            show=False,
            callback=cb.load_file_callback, 
            width=DW // 2, 
            height=DH // 2, 
            default_path=default_dataset_path,
            ):
        d.add_file_extension('.*')
        d.add_file_extension('', color=(200, 200, 255, 255))
        d.add_file_extension('.csv', color=(200, 255, 200, 255))

    with d.group(horizontal=True, parent=WorkspaceWindowTag.CONSTRUCTOR):
        with d.child_window(tag="WindowNodeEditor", width=int(DW / 1.5)):
            with d.node_editor(
                    tag="NE", 
                    callback=cb.link_callback, 
                    delink_callback=cb.delink_callback,
                    minimap_location=d.mvNodeMiniMap_Location_BottomRight,
            ):
                pass

        with d.group():
            with d.child_window(tag='WindowHyperparams', height=int(DH / 3.5)):
                window_width = int(DW - DW / 1.5)
                label_indent = window_width // 3
                d.add_spacer(height=int(indent / 2.5))
                d.add_text('Hyperparams', tag='HyperparamsTextLabel', indent=label_indent)
                d.add_spacer(height=int(indent / 2.5))
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
                d.add_spacer(height=int(indent / 2.5))
                d.add_separator()
                d.add_spacer(height=int(indent / 2.5))
                d.add_text('DataSet', tag='DatasetLabel', indent=label_indent)
                d.add_spacer(height=int(indent / 2.5))
                with d.group(horizontal=True):
                    d.add_button(
                            tag='DatasetLoadButton', 
                            label='Load', 
                            callback=cb.choice_dataset_callback, 
                            width=BUTTON_WIDTH_HYPERPARAMS, 
                            indent=indent
                             )
                    d.add_button(
                            tag='DatasetCreateButton', 
                            label='Create', 
                            callback=cb.choice_dataset_callback, 
                            width=BUTTON_WIDTH_HYPERPARAMS, 
                            indent=indent + BUTTON_WIDTH_HYPERPARAMS + PADDING_BUTTONS_HYPERPARAMS,
                             )
                    d.add_combo(
                            tag='TargetColumn', 
                            width=DW // 15, 
                            items=["Choose dataset"], 
                            default_value='[Target]',
                            indent=(indent + PADDING_BUTTONS_HYPERPARAMS + BUTTON_WIDTH_HYPERPARAMS)*2,
                            )
                    d.add_button(
                            tag='train', 
                            label='Train', 
                            width=DW // 20, 
                            indent=(indent + PADDING_BUTTONS_HYPERPARAMS + BUTTON_WIDTH_HYPERPARAMS)*3 + 100,
                            )

            with d.child_window(tag='TableWindow'):
                pass
