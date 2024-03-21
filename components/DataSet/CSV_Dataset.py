import pandas as pd
from torch.utils.data import Dataset
import torch

import config


class CSV_Dataset(Dataset):
    def __init__(self, csv_path, target_column):
        df = pd.read_csv(csv_path)
        self.Y = df[target_column]
        self.X = df.drop(columns=[target_column])

    def __len__(self):
        return len(self.Y)

    def mean(self):
        return self.Y.mean()

    def __getitem__(self, item):
        series = self.X.iloc[item, :]
        return torch.from_numpy(series.values), self.Y[item]


if __name__ == '__main__':
    df = pd.read_csv(config.test_path)
    print(df.columns)
    print((df["charges"].apply(lambda a: abs(a - 13000))).mean())


