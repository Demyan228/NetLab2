from itertools import count


def _tags_generator():
    for idx in count(1):
        yield f'autotag-{idx}'
_utag = _tags_generator()


def get_tag():
    return next(_utag)


class Tags:
    CONSTRUCTOR = get_tag()
    DATASET_TARGET_COLUMN = get_tag()
    DATASET_TABLE = get_tag()
    PRIMARY_WINDOW = get_tag()
    START_TRAIN_BUTTON = get_tag()
    SWITCH_PANEL_WINDOW = get_tag()
    TABLE_PRESENTATION_WINDOW = get_tag()
    TEST_LOSS_SERIES = get_tag()
    TRAIN = get_tag()
    TRAIN_LOSS_SERIES = get_tag()
    TRAIN_PLOT_X_AXIS = get_tag()
    TRAIN_PLOT_Y_AXIS = get_tag()


class CreateDatasetTags:
    CREATOR_WINDOW = get_tag()
    CLASSIFICATION = get_tag()
    REGRESSION = get_tag()

    N_SAMPLES = get_tag()
    N_FEATURES = get_tag()
    N_CLASSES = get_tag()

