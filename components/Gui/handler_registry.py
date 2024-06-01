from dearpygui import dearpygui as d
from components.Gui import callbacks as cb


def init_handler_registry():
    with d.handler_registry():
        d.add_mouse_click_handler(callback=cb.show_node_menu_callback, button=1)
        d.add_key_press_handler(key=d.mvKey_M, callback=cb.visible_map_callback)
        d.add_key_press_handler(key=d.mvKey_Delete, callback=cb.delete_key_pressed_callback)
