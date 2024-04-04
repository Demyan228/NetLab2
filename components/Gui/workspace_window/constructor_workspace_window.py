import dearpygui.dearpygui as d
from numpy import random
import config as main_config
import components.Gui.config as gui_config
import components.Gui.callbacks as cb
from components.Gui.tags import Tags


def create_dataset_callback(sender, app_data):
    padding = ' '
    with d.window(modal=True):
        with d.tab_bar():
            with d.tab(label='Classification'):
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                with d.group(horizontal=True):
                    samples_tag = 'SamplesTag'
                    def set_samples_value_cb(sender, _, value):
                        d.set_value(samples_tag, value)
                    d.add_text(' Samples: ')
                    d.add_text(padding)
                    d.add_slider_int(tag=samples_tag, default_value=100, width=100, max_value=10000)
                    d.add_text(padding)
                    d.add_button(label='10', width=100, callback=set_samples_value_cb, user_data=10)
                    d.add_button(label='100', width=100, callback=set_samples_value_cb, user_data=100)
                    d.add_button(label='1000', width=100, callback=set_samples_value_cb, user_data=1000)
                with d.group(horizontal=True):
                    features_tag = 'FeaturesTag'
                    def set_features_value_cb(sender, _, value):
                        d.set_value(features_tag, value)
                    d.add_text(' Features:')
                    d.add_text(padding)
                    d.add_slider_int(tag=features_tag, default_value=4, width=100)
                    d.add_text(padding)
                    d.add_button(label='2', width=100, callback=set_features_value_cb, user_data=2)
                    d.add_button(label='4', width=100, callback=set_features_value_cb, user_data=4)
                    d.add_button(label='8', width=100, callback=set_features_value_cb, user_data=8)
                with d.group(horizontal=True):
                    classes_tag = 'ClassesTag'
                    def set_classes_value_cb(sender, _, value):
                        d.set_value(classes_tag, value)
                    d.add_text(' Classes: ')
                    d.add_text(padding)
                    d.add_slider_int(tag=classes_tag, default_value=2, width=100)
                    d.add_text(padding)
                    d.add_button(label='2', width=100, callback=set_classes_value_cb, user_data=2)
                    d.add_button(label='4', width=100, callback=set_classes_value_cb, user_data=4)
                    d.add_button(label='8', width=100, callback=set_classes_value_cb, user_data=8)
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                with d.group(horizontal=True):
                    d.add_text(' Random State:')
                    d.add_text(padding)
                    d.add_input_int(default_value=random.randint(1, 1_000_000_000), step=0, width=300)
                    d.add_text(' ')
                    d.add_checkbox(default_value=True)
            with d.tab(label='Regression'):
                pass

        d.add_spacer(height=int(gui_config.INDENT / 2.5))
        with d.group(horizontal=True):
            d.add_button(label='Random', indent=20, width=180)
            d.add_text(' ')
            d.add_button(label='Create', width=180)
            d.add_text(' ')
            d.add_button(label='Cancel', width=180)
        d.add_spacer(height=int(gui_config.INDENT / 5))


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
            with d.child_window(tag='WindowHyperparams', height=int(main_config.DH / 2.5)):
                window_width = int(main_config.DW - main_config.DW / 1.5)
                label_indent = window_width // 3
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                d.add_text('Hyperparams', tag='HyperparamsTextLabel', indent=label_indent)
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                d.add_input_double(tag='HyperparamsLearningRate', label=' LearningRate', width=main_config.DW // 10, indent=gui_config.INDENT,
                                  min_value=0.000001, default_value=0.001, step=0)
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
                            callback=create_dataset_callback, 
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
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                d.add_separator()
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                d.add_text('[Train / Val / Test]', indent=label_indent // 2)
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                with d.group(horizontal=True):
                    d.add_drag_floatx(size=3, default_value=(70, 15, 15), indent=gui_config.INDENT)
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                with d.group(horizontal=True):
                    d.add_checkbox(label=' KFolds', indent=gui_config.INDENT)
                    d.add_text('         ')
                    d.add_button(label='5', width=100)
                    d.add_button(label='8', width=100)
                    d.add_button(label='10', width=100)
                    d.add_text('    ')
                    d.add_input_int(default_value=5, width=100, step=0)

            with d.child_window(tag='TableWindow'):
                pass
