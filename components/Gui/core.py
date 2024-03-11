from collections import defaultdict
import config
import os

links_graph = defaultdict(list)
links_elements = {}
current_dataset_path = os.path.join(config.default_dataset_path, "test.csv")
def change_dataset_path(path):
    global current_dataset_path
    current_dataset_path = path