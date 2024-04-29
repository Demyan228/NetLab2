import os
from screeninfo import get_monitors


###     LOG      ###
debug = True

###    GUI    ###
monitor = get_monitors()[0]
DW, DH = monitor.width, monitor.height - 50
FPS = 20

MAIN_FONT = os.path.join('resources', 'font.ttf')
MAIN_FONT_SIZE = 40



###   DATA   ###
default_dataset_path = 'C:\\Users\\bubno\\Downloads'
TEST_DATASET = 'netlab_test.csv'
model_structs_path = 'model_structs'
if not os.path.exists(model_structs_path):
    os.mkdir(model_structs_path)

###   TRAIN   ###
default_train_epochs = 100
default_lr = 0.01
default_optimizer = "Adam"
default_criterian = "MAE"


if os.name == 'posix':
    DH += 50
    default_dataset_path = '/home/user/datasets/'
    TEST_DATASET = 'test.csv'
