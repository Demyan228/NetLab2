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

FPS = 60

###   TRAIN   ###
default_train_epochs = 3
default_train_batches = 2
default_lr = 0.001
### ASSEMBLER ###
