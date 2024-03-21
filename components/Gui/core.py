from collections import defaultdict
import config
import os

def change_dataset_path(path):
    global current_dataset_path
    current_dataset_path = path

current_dataset_path = os.path.join(config.default_dataset_path, config.TEST_DATASET)
links_graph = defaultdict(list)
links_elements = {}
