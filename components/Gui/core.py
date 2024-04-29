from collections import defaultdict
import config
import os


def change_dataset_path(path):
    global current_dataset_path
    current_dataset_path = path


def get_saved_model_names():
    return os.listdir(config.model_structs_path)


current_dataset_path = os.path.join(config.default_dataset_path, config.TEST_DATASET)
all_nodes_tags = []
links_graph = defaultdict(list)
links_elements = {}
