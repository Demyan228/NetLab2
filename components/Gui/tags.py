from itertools import count


def _tags_generator():
    for idx in count(1):
        yield f'autotag-{idx}'
_utag = _tags_generator()


def get_tag():
    return next(_utag)


class Tags:
    PRIMARY_WINDOW = get_tag()
    SWITCH_PANEL_WINDOW = get_tag()
    CONSTRUCTOR = get_tag()
    TRAIN = get_tag()
    TRAIN_LOSS_SERIES = get_tag()
    TEST_LOSS_SERIES = get_tag()
    START_TRAIN_BUTTON = get_tag()
    TRAIN_PLOT_X_AXIS = get_tag()
    TRAIN_PLOT_Y_AXIS = get_tag()

