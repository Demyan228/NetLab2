from win32api import GetSystemMetrics
###     LOG      ###
debug = False

###    GUI    ###
DW, DH = GetSystemMetrics(0), GetSystemMetrics(1) - 50
indent = DW // 60

FPS = 60

###   TRAIN   ###
default_train_epochs = 3
default_train_batches = 2
default_lr = 0.001
### ASSEMBLER ###
