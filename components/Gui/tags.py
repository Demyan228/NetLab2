from itertools import count


def _tags_generator():
    for idx in count(1):
        yield f'autotag-{idx}'
_utag = _tags_generator()


def get_tag():
    return next(_utag)


class Tags:
    WW_TRAIN = get_tag()
    WW_CONSTRUCTOR = get_tag()
    WW_ENSEMBLE = get_tag()
    WW_DATA_ANALYSIS = get_tag()

    DATASET_TARGET_COLUMN = get_tag()
    DATASET_TABLE = get_tag()
    PRIMARY_WINDOW = get_tag()
    START_TRAIN_BUTTON = get_tag()
    SWITCH_PANEL_WINDOW = get_tag()
    TABLE_PRESENTATION_WINDOW = get_tag()
    VAL_LOSS_SERIES = get_tag()
    SPLITS_HYPERPARAMS = get_tag()
    TEXT_EPOCH_LABEL = get_tag()
    TEXT_TRAIN_ACC = get_tag()
    TEXT_TRAIN_LOSS = get_tag()
    TEXT_VAL_ACC = get_tag()
    TEXT_VAL_LOSS = get_tag()
    TRAIN_LOSS_SERIES = get_tag()
    TRAIN_PLOT_PROGRESS = get_tag()
    TRAIN_PLOT_X_AXIS = get_tag()
    TRAIN_PLOT_Y_AXIS = get_tag()


class CreateDatasetTags:
    CREATOR_WINDOW = get_tag()
    CLASSIFICATION = get_tag()
    REGRESSION = get_tag()

    REG_RANDOM_SEED = get_tag()
    CLS_RANDOM_SEED = get_tag()

    N_CLS_SAMPLES = get_tag()
    N_CLS_FEATURES = get_tag()
    N_CLS_CLASSES = get_tag()

    N_REG_SAMPLES = get_tag()
    N_REG_FEATURES = get_tag()
    N_REG_CLASSES = get_tag()

