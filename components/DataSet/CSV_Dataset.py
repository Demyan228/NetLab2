import pandas as pd
from torch.utils.data import Dataset
import torch


class CSV_Dataset(Dataset):
    def __init__(self, csv_path, target_column):
        df = pd.read_csv(csv_path)
        self.Y = df[target_column]
        self.X = df.drop(columns=[target_column])

    def __len__(self):
        return len(self.Y)

    def __getitem__(self, item):
        series = self.X.iloc[item, :]
        return torch.from_numpy(series.values), self.Y[item]


