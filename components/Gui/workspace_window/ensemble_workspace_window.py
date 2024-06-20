import dearpygui.dearpygui as d
from components.Gui.tags import Tags


def load_ensemble_workspace():
    with d.child_window(parent=Tags.WW_ENSEMBLE):
        d.add_text('  Ensemble Comming soon..')
