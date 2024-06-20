from numpy import random
from sklearn import os
import common
import sklearn.datasets
import pandas as pd
import dearpygui.dearpygui as d

from components.Gui.core import change_dataset_path
import config as main_config
import components.Gui.config as gui_config
import components.Gui.callbacks as cb
from components.Gui.tags import Tags, CreateDatasetTags as CTags


class DatasetCreator:

    _current_dataset_type = CTags.CLASSIFICATION

    @staticmethod
    def change_dataset_type_callback(sender, app_data):
        DatasetCreator._current_dataset_type = d.get_item_alias(app_data)

    @staticmethod
    def _create_dataset_classification():
        n_samples = d.get_value(CTags.N_CLS_SAMPLES)
        n_features = d.get_value(CTags.N_CLS_FEATURES)
        n_classes = d.get_value(CTags.N_CLS_CLASSES)
        random_seed = d.get_value(CTags.CLS_RANDOM_SEED)
        data_x, data_y = sklearn.datasets.make_classification(
                n_samples=n_samples,
                n_features=n_features,
                n_classes=n_classes,
                random_state=random_seed
                )
        dataset = pd.DataFrame(data_x, columns=[f' FEATURE-{i} ' for i in range(1, n_features + 1)])
        dataset['TARGET'] = pd.Series(data_y)
        if not os.path.exists(main_config.TMP_FOLDER_PATH):
            os.makedirs(main_config.TMP_FOLDER_PATH)
        dataset.to_csv(main_config.CUSTOM_DATASET_PATH, index=False)
        cb.create_csv_table(main_config.CUSTOM_DATASET_PATH)
        change_dataset_path(main_config.CUSTOM_DATASET_PATH)

    @staticmethod
    def _create_dataset_regression():
        n_samples = d.get_value(CTags.N_REG_SAMPLES)
        n_features = d.get_value(CTags.N_REG_FEATURES)
        random_seed = d.get_value(CTags.REG_RANDOM_SEED)
        data_x, data_y = sklearn.datasets.make_regression(
                n_samples=n_samples,
                n_features=n_features,
                random_state=random_seed
                )
        dataset = pd.DataFrame(data_x, columns=[f' FEATURE-{i} ' for i in range(1, n_features + 1)])
        dataset['TARGET'] = pd.Series(data_y)
        if not os.path.exists(main_config.TMP_FOLDER_PATH):
            os.makedirs(main_config.TMP_FOLDER_PATH)
        dataset.to_csv(main_config.CUSTOM_DATASET_PATH, index=False)
        cb.create_csv_table(main_config.CUSTOM_DATASET_PATH)
        change_dataset_path(main_config.CUSTOM_DATASET_PATH)

    @staticmethod
    def create_dataset_callback(sender, app_data, user_data):
        {
            CTags.CLASSIFICATION: DatasetCreator._create_dataset_classification,
            CTags.REGRESSION: DatasetCreator._create_dataset_regression,
        }[DatasetCreator._current_dataset_type]()
        d.hide_item(CTags.CREATOR_WINDOW)



def create_dataset_regression(n_samples: int, n_features: int, n_outputs: int):
    pass


def create_dataset_window_callback(sender, app_data):
    padding = ' '
    if d.does_alias_exist(CTags.CREATOR_WINDOW):
        d.show_item(CTags.CREATOR_WINDOW)
        return
    with d.window(tag=CTags.CREATOR_WINDOW, modal=True):
        with d.tab_bar(tag='TB', callback=DatasetCreator.change_dataset_type_callback):
            with d.tab(label='Classification', tag=CTags.CLASSIFICATION):
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                with d.group():
                    with d.group(horizontal=True):
                        def set_samples_value_cb(sender, _, value):
                            d.set_value(CTags.N_CLS_SAMPLES, value)
                        d.add_text(' Samples: ')
                        d.add_text(padding)
                        d.add_slider_int(tag=CTags.N_CLS_SAMPLES, default_value=100, width=100, max_value=10000)
                        d.add_text(padding)
                        d.add_button(label='10', width=100, callback=set_samples_value_cb, user_data=10)
                        d.add_button(label='100', width=100, callback=set_samples_value_cb, user_data=100)
                        d.add_button(label='1000', width=100, callback=set_samples_value_cb, user_data=1000)
                    with d.group(horizontal=True):
                        def set_features_value_cb(sender, _, value):
                            d.set_value(CTags.N_CLS_FEATURES, value)
                        d.add_text(' Features:')
                        d.add_text(padding)
                        d.add_slider_int(tag=CTags.N_CLS_FEATURES, default_value=4, width=100)
                        d.add_text(padding)
                        d.add_button(label='2', width=100, callback=set_features_value_cb, user_data=2)
                        d.add_button(label='4', width=100, callback=set_features_value_cb, user_data=4)
                        d.add_button(label='8', width=100, callback=set_features_value_cb, user_data=8)
                    with d.group(horizontal=True):
                        def set_classes_value_cb(sender, _, value):
                            d.set_value(CTags.N_CLS_CLASSES, value)
                        d.add_text(' Classes: ')
                        d.add_text(padding)
                        d.add_slider_int(tag=CTags.N_CLS_CLASSES, default_value=2, width=100)
                        d.add_text(padding)
                        d.add_button(label='2', width=100, callback=set_classes_value_cb, user_data=2)
                        d.add_button(label='4', width=100, callback=set_classes_value_cb, user_data=4)
                        d.add_button(label='8', width=100, callback=set_classes_value_cb, user_data=8)
                    d.add_spacer(height=int(gui_config.INDENT / 2.5))
                    with d.group(horizontal=True):
                        d.add_text(' Random Seed:')
                        d.add_text(padding)
                        d.add_input_int(
                                tag=CTags.CLS_RANDOM_SEED, 
                                default_value=random.randint(1, 1_000_000_000), 
                                step=0, width=395
                                )
                        d.add_text(padding)
            with d.tab(label='Regression', tag=CTags.REGRESSION):
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                with d.group():
                    with d.group(horizontal=True):
                        def set_samples_value_cb(sender, _, value):
                            d.set_value(CTags.N_REG_SAMPLES, value)
                        d.add_text(' Samples: ')
                        d.add_text(padding)
                        d.add_slider_int(tag=CTags.N_REG_SAMPLES, default_value=100, width=100, max_value=10000)
                        d.add_text(padding)
                        d.add_button(label='10', width=100, callback=set_samples_value_cb, user_data=10)
                        d.add_button(label='100', width=100, callback=set_samples_value_cb, user_data=100)
                        d.add_button(label='1000', width=100, callback=set_samples_value_cb, user_data=1000)
                    with d.group(horizontal=True):
                        def set_features_value_cb(sender, _, value):
                            d.set_value(CTags.N_REG_FEATURES, value)
                        d.add_text(' Features:')
                        d.add_text(padding)
                        d.add_slider_int(tag=CTags.N_REG_FEATURES, default_value=4, width=100)
                        d.add_text(padding)
                        d.add_button(label='2', width=100, callback=set_features_value_cb, user_data=2)
                        d.add_button(label='4', width=100, callback=set_features_value_cb, user_data=4)
                        d.add_button(label='8', width=100, callback=set_features_value_cb, user_data=8)
                    d.add_spacer(height=int(gui_config.INDENT * 1.175))
                    with d.group(horizontal=True):
                        d.add_text(' Random Seed:')
                        d.add_text(padding)
                        d.add_input_int(
                                tag=CTags.REG_RANDOM_SEED, 
                                default_value=random.randint(1, 1_000_000_000), 
                                step=0, width=395
                                )
                        d.add_text(padding)

        d.add_spacer(height=int(gui_config.INDENT / 2.5))
        with d.group(horizontal=True):
            d.add_button(
                    label='Create', 
                    width=gui_config.DEFAULT_BUTTON_WIDTH, 
                    callback=DatasetCreator.create_dataset_callback,
                    indent=gui_config.INDENT // 4,
                    )
            d.add_text(' ')
            d.add_button(
                    label='Cancel', 
                    width=gui_config.DEFAULT_BUTTON_WIDTH, 
                    callback=lambda _: d.hide_item(CTags.CREATOR_WINDOW),
                    )
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


    with d.file_dialog(
            tag='STRUCT_FILEDIALOG',
            directory_selector=False,
            show=False,
            callback=cb.load_model_struct_callback,
            width=main_config.DW // 2,
            height=main_config.DH // 2,
            default_path=main_config.model_structs_path,
            ):
        d.add_file_extension('.*')
        d.add_file_extension('', color=(200, 255, 200, 255))

    with d.group(horizontal=True, parent=Tags.WW_CONSTRUCTOR):
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
                d.add_input_double(tag='HyperparamsLearningRate', label=' LearningRate', width=main_config.DW // 10, 
                        indent=gui_config.INDENT, min_value=0.000001, default_value=0.001, step=0, format='%.7f')
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
                with d.group():
                    with d.group(horizontal=True):
                        d.add_button(
                                label='Load', 
                                callback=cb.choice_dataset_callback, 
                                width=gui_config.HYPERPARAMS_BUTTON_WIDTH, 
                                indent=gui_config.INDENT
                                 )
                        d.add_button(
                                label='Create', 
                                callback=create_dataset_window_callback, 
                                width=gui_config.HYPERPARAMS_BUTTON_WIDTH, 
                                indent=gui_config.INDENT + gui_config.HYPERPARAMS_BUTTON_WIDTH + gui_config.PADDING_BUTTONS_HYPERPARAMS,
                                 )
                        d.add_combo(
                                tag=Tags.DATASET_TARGET_COLUMN,
                                width=main_config.DW // 15, 
                                items=["Choose dataset"], 
                                default_value='[Target]',
                                indent=(gui_config.INDENT + gui_config.PADDING_BUTTONS_HYPERPARAMS + gui_config.HYPERPARAMS_BUTTON_WIDTH)*2,
                                )
                        d.add_button(
                                tag=Tags.START_TRAIN_BUTTON, 
                                label='Train', 
                                width=main_config.DW // 20, 
                                indent=(gui_config.INDENT + gui_config.PADDING_BUTTONS_HYPERPARAMS + gui_config.HYPERPARAMS_BUTTON_WIDTH)*3,
                                )

                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                d.add_separator()
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                d.add_text('[Train / Val / Test]', indent=label_indent // 2)
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                with d.group(horizontal=True):
                    d.add_drag_floatx(tag=Tags.SPLITS_HYPERPARAMS, size=3, 
                                      default_value=(70, 15, 15), indent=gui_config.INDENT)
                d.add_spacer(height=int(gui_config.INDENT / 2.5))
                with d.group(horizontal=True):
                    d.add_checkbox(label=' KFolds', indent=gui_config.INDENT)
                    d.add_text('         ')
                    d.add_button(label='5', width=100)
                    d.add_button(label='8', width=100)
                    d.add_button(label='10', width=100)
                    d.add_text('    ')
                    d.add_input_int(default_value=5, width=100, step=0)

            with d.child_window(tag=Tags.TABLE_PRESENTATION_WINDOW):
                pass
