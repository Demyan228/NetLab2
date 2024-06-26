import math
import dearpygui.dearpygui as d
from common import log
import config as main_config
import components.Gui.config as gui_config
import components.Gui.callbacks as cb
from components.Gui.tags import Tags
from event_system import EventSystem as es, EventTypes


PLOT_WIDTH = int(main_config.DW * 2 / 3)
PLOT_HEIGHT = main_config.DH // 2

tr_X = list(map(float, range(1, 100)))
tr_Y = list(map(math.sqrt, tr_X))

ts_X = list(map(float, range(1, 100)))
ts_Y = [math.sqrt(i) / 2 for i in ts_X]

def load_train_workspace():
    with d.child_window(parent=Tags.WW_TRAIN):
        with d.group():
            d.add_spacer(height=gui_config.INDENT // 2)
            with d.group(horizontal=True):
                indent = (main_config.DW - gui_config.DEFAULT_BUTTON_WIDTH * 3) // 2
                d.add_button(label='Pause', width=gui_config.DEFAULT_BUTTON_WIDTH, indent=indent, height=70)
                d.add_button(tag='next_button', label='Next >>', width=gui_config.DEFAULT_BUTTON_WIDTH, height=70)
                d.add_button(label='Stop', width=gui_config.DEFAULT_BUTTON_WIDTH, height=70)
        d.add_spacer(height=gui_config.INDENT // 2)
        d.add_separator()
        with d.tab_bar():
            with d.tab(label='Full'):
                with d.child_window():
                    with d.group(horizontal=True):
                        with d.plot(width=PLOT_WIDTH, height=PLOT_HEIGHT):
                            d.add_plot_legend()

                            d.add_plot_axis(d.mvXAxis, tag=Tags.TRAIN_PLOT_X_AXIS)
                            d.add_plot_axis(d.mvYAxis, tag=Tags.TRAIN_PLOT_Y_AXIS)

                            d.add_line_series([], [], tag=Tags.TRAIN_LOSS_SERIES, 
                                              label='Train Loss', parent=Tags.TRAIN_PLOT_Y_AXIS)
                            d.add_line_series([], [], tag=Tags.VAL_LOSS_SERIES, 
                                              label='Val Loss', parent=Tags.TRAIN_PLOT_Y_AXIS)
                        d.add_text('    ')
                        with d.group(width=200):
                            d.add_text(tag=Tags.TEXT_EPOCH_LABEL)
                            d.add_spacer(height=5)
                            d.add_separator()
                            d.add_spacer(height=5)
                            d.add_text(tag=Tags.TEXT_TRAIN_LOSS)
                            d.add_text(tag=Tags.TEXT_VAL_LOSS)
                            d.add_spacer(height=5)
                            d.add_separator()
                            d.add_spacer(height=5)
                            d.add_text(tag=Tags.TEXT_TRAIN_ACC)
                            d.add_text(tag=Tags.TEXT_VAL_ACC)

                    d.add_progress_bar(tag=Tags.TRAIN_PLOT_PROGRESS, width=PLOT_WIDTH)
            with d.tab(label='Other'):
                pass


@es.subscribe(EventTypes.EPOCH_DONE)
async def update_series(event_data):
    history = event_data["history"]
    train_X = list(range(1, len(history.train_loss) + 1))
    val_X = list(range(1, len(history.val_loss) + 1))
    d.set_value(Tags.TRAIN_LOSS_SERIES, [train_X, history.train_loss])
    d.set_value(Tags.VAL_LOSS_SERIES, [val_X, history.val_loss])
    d.fit_axis_data(Tags.TRAIN_PLOT_X_AXIS)
    d.fit_axis_data(Tags.TRAIN_PLOT_Y_AXIS)
    current_progress_idx = event_data['progress_params']['current_iteration_idx'] + 1
    max_iterations = event_data['progress_params']['max_iterations']
    d.set_value(Tags.TRAIN_PLOT_PROGRESS, current_progress_idx / max_iterations)
    d.set_value(Tags.TEXT_EPOCH_LABEL, f'Epoch: {current_progress_idx} / {max_iterations}')
    d.set_value(Tags.TEXT_TRAIN_LOSS, f'Train loss: {history.train_loss[-1]:.4f}')
    d.set_value(Tags.TEXT_VAL_LOSS, f'  Val loss: {history.val_loss[-1]:.4f}')
    d.set_value(Tags.TEXT_TRAIN_ACC, f' Train acc: ...')
    d.set_value(Tags.TEXT_VAL_ACC, f'   Val acc: ...')
