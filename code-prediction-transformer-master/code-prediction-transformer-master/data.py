import utils
import json
import pickle

from torch.utils.data import Dataset

class CodeDataset(Dataset):
    def __init__(self):
        self.inputs = []

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, index):
        # Add padding?
        return self.inputs[index]

    def cache_dataset(self, dest_path):
        with open(dest_path, "wb") as fout:
            pickle.dump(self.inputs, fout)

    def load_from_cache(self, cache_path):
        with open(cache_path, "rb") as fin:
            self.inputs = pickle.load(fin)

    def load_from_file(self, file_path):
        with open(file_path) as fin:
            for line in utils.file_tqdm(fin):
                self.inputs.append([int(s) for s in line.split()])