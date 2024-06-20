import dearpygui.dearpygui as d
from components.Gui.tags import Tags


def load_data_analysis_workspace():
    with d.child_window(parent=Tags.WW_DATA_ANALYSIS):
        d.add_text('  Data analysis Comming soon..')
