import os
from screeninfo import get_monitors


###     LOG      ###
debug = True

###    GUI    ###
monitor = get_monitors()[0]
DW, DH = monitor.width, monitor.height - 50
indent = DW // 60
FPS = 20

MAIN_FONT = os.path.join('resources', 'font.ttf')
MAIN_FONT_SIZE = 40

SWITCH_PANEL_BUTTON_WIDTH = 300


###   DATA   ###
default_dataset_path = 'C:\\Users\\bubno\\Downloads'
TEST_DATASET = 'netlab_test.csv'


###   TRAIN   ###
default_train_epochs = 50
default_lr = 0.01
default_optimizer = "Adam"
default_criterian = "MAE"


if os.name == 'posix':
    DH += 50
    default_dataset_path = '~/datasets/'
    TEST_DATASET = 'test.csv'
