from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
import os
import pathlib
import random

import pandas as pd
from torch.utils.data import DataLoader as PytorchDataLoader, Dataset as PytorchDataSet
from torchvision import datasets as torchvision_datasets, torch, transforms as torchvision_transforms
from torchvision.datasets.folder import pil_loader

from common import log


class DatasetType(Enum):
    CSV     = auto()
    IMG     = auto()
    INVALID = auto()


def _is_img_dataset(path: str) -> bool:
    if not os.path.isdir(path):
        return False
    return all(os.path.isdir(os.path.join(path, name)) for name in os.listdir(path))


def get_dataset_type(path: str) -> DatasetType:

    if not os.path.exists(path):
        raise ValueError(f'Incorrect path {path}')

    if pathlib.Path(path).suffix.lower() == '.csv':
        return DatasetType.CSV

    if _is_img_dataset(path):
        return DatasetType.IMG

    return DatasetType.INVALID


def is_valid_dataset(what) -> bool: # TODO
    return False


@dataclass
class DataSet:
    
    train: PytorchDataSet
    val: PytorchDataSet
    test: PytorchDataSet
    batch_size: int
    
    def train_loader(self) -> PytorchDataLoader: 
        return PytorchDataLoader(self.train, batch_size=self.batch_size)

    def val_loader(self) -> PytorchDataLoader: 
        return PytorchDataLoader(self.val, batch_size=self.batch_size)

    def test_loader(self) -> PytorchDataLoader: 
        return PytorchDataLoader(self.test, batch_size=self.batch_size)


class CSVPytorchDataSet(PytorchDataSet):

    def __init__(self, df: pd.DataFrame, labels_column: str):
        self.features = df.drop(columns=[labels_column]).reset_index(drop=True)
        self.labels = df[labels_column].reset_index(drop=True)

    def __getitem__(self, idx):
        features = torch.tensor(self.features.loc[idx, :].tolist())
        labels = torch.tensor(self.labels.loc[idx].tolist())
        return features, labels

    def __len__(self):
        return len(self.labels)


class ImgPytorchDataSet(PytorchDataSet):

    @dataclass
    class ImgSample:
        path: str
        label: int

    def __init__(self, samples: list[ImgSample]):
        self.samples = samples
        self.transforms = torchvision_transforms.Compose([torchvision_transforms.ToTensor(), torchvision_transforms.Resize([64, 64])])

    def __getitem__(self, idx):
        sample = self.samples[idx]
        image = pil_loader(sample.path)
        label = sample.label
        image = self.transforms(image)
        return image, label

    def __len__(self):
        return len(self.samples)


def _get_img_dataset(dataset_path: str, splits: list[float], batch_size) -> DataSet:
    samples: list[ImgPytorchDataSet.ImgSample] = []
    for label_idx, label in enumerate(os.listdir(dataset_path)):
        label_path = os.path.join(dataset_path, label)
        for img_file_name in os.listdir(label_path):
            img_path = os.path.join(label_path, img_file_name)
            sample = ImgPytorchDataSet.ImgSample(img_path, label_idx)
            samples.append(sample)
    random.shuffle(samples)
    data_size = len(samples)
    
    left, right = 0, int(data_size * splits[0])
    train_samples = samples[left:right]
    train_part = ImgPytorchDataSet(train_samples)

    left, right = right, int(data_size * splits[1])
    val_samples = samples[left:right]
    val_part = ImgPytorchDataSet(val_samples)

    left, right = right, int(data_size * splits[2])
    test_samples = samples[left:right]
    test_part = ImgPytorchDataSet(test_samples)

    return DataSet(train_part, val_part, test_part, batch_size)


def _get_csv_dataset(dataset_path: str, labels: str, splits: list[float], batch_size) -> DataSet:
    df = pd.read_csv(dataset_path)
    df = df.sample(frac=1).reset_index(drop=True)
    l = len(df)
    splits = [0] + splits
    parts = list(map(int, [l*i for i in splits]))

    left, right = parts[0], parts[1]
    train_df = df.loc[left:right, :]
    train_part = CSVPytorchDataSet(train_df, labels)

    left, right = right, right + parts[2]
    val_df = df.loc[left:right, :]
    val_part = CSVPytorchDataSet(val_df, labels)

    left, right = right, right + parts[3]
    test_df = df.loc[left:right, :]
    test_part = CSVPytorchDataSet(test_df, labels)

    return DataSet(train_part, val_part, test_part, batch_size)


def get_dataset(dataset_parameters: dict) -> DataSet:
    #dataset_parameters = {'path': '/home/user/datasets/test.csv', 'target_column': 'charges', 'splits': [0.8, 0.1, 0.1], 'batch_size': 64} 
    dataset_path = dataset_parameters['path']
    splits = dataset_parameters['splits']
    dataset_type = get_dataset_type(dataset_path)
    batch_size = dataset_parameters['batch_size']

    match dataset_type:
        case DatasetType.CSV: 
            labels = dataset_parameters['target_column']
            return _get_csv_dataset(dataset_path, labels, splits, batch_size)
        case DatasetType.IMG:
            return _get_img_dataset(dataset_path, splits, batch_size)
        case DatasetType.INVALID:
            raise ValueError(f'Invalid dataset {dataset_path}')
        case _:
            assert False, 'Never'


if __name__ == '__main__':
    TEST_DATASET = 'test.csv'
    default_dataset_path = '/home/user/datasets/'
    dpath = os.path.join(default_dataset_path, TEST_DATASET)
    df = pd.read_csv(dpath)
    d = CSVPytorchDataSet(df, 'charges')
    f = d.features.loc[0, :].to_list()
    l = d.labels[0]
    f = torch.tensor(f)
    l = torch.tensor(l)
    print(df.loc[5:7, :])

