import os

from screeninfo import get_monitors


###     LOG      ###
debug = True

###    GUI    ###
monitor = get_monitors()[0]
DW, DH = monitor.width, monitor.height
if os.name == "nt":
    DH -= 50

indent = DW // 60
FPS = 20

###   DATA   ###

default_dataset_path = 'C:\\Users\\bubno\\Downloads'

###   TRAIN   ###
default_train_epochs = 50
default_lr = 0.01
default_optimizer = "Adam"
default_criterian = "MAE"
### ASSEMBLER ###
