import h5py
import numpy as np
from PIL import Image
import torch
import torch.utils.data as Data

class HDF5Dataset(Data.Dataset):


    def __init__(self, file_path, datasets: tuple, transform=None):
        super().__init__()

        self.file_path = file_path
        self.datasets = datasets

        self.transform = transform

        with h5py.File(self.file_path) as file:
            self.length = len(file[self.datasets[0]])
            self.target = file[self.datasets[1]][0]
            # print(f'self.target: {self.target}')

    def _open_hdf5(self):
        self._hf = h5py.File(self.file_path, 'r')

    def __getitem__(self, index) :
        if not hasattr(self, '_hf'):
            self._open_hdf5()

        # get data
        x = self._hf[self.datasets[0]][index]
        x = Image.fromarray(np.array(x))

        if self.transform:
            x = self.transform(x)
        else:
            x = torch.from_numpy(x)

        return x

    def __len__(self):
        return self.length

class CacheHDF5Dataset(Data.Dataset):


    def __init__(self, file_path, datasets: tuple, transform=None, batch_size=None, nbatch=10):
        super().__init__()

        self.file_path = file_path
        self.datasets = datasets

        self.transform = transform
        self.batch_size = batch_size
        self.nbatch = nbatch
        # self.file = h5py.File(self.file_path, 'r')
        self.length = len(h5py.File(self.file_path, 'r')[self.datasets[0]])

        self.tail_idx = 0
        self.head_idx = (self.tail_idx + 10*self.batch_size)

        if self.head_idx > self.length and \
            (self.length - self.tail_idx) > 0:
            self.head_idx = self.length

        self._gen_new_data()
        # self.data = h5py.File(self.file_path, 'r')[self.datasets[0]][self.tail_idx:self.head_idx]
        self._gen_new_idxs()

    def _gen_new_idxs(self):
        self.tail_idx += 10*self.batch_size
        self.head_idx += 10*self.batch_size

        if self.tail_idx > self.length:
            self.tail_idx = 0
            self.tail_idx = self.nbatch * self.batch_size 
        elif self.head_idx > self.length and \
            (self.length - self.tail_idx) > 0:
            self.head_idx = self.length
        
    def _gen_new_data(self):
        self.data = h5py.File(self.file_path, 'r')[self.datasets[0]][self.tail_idx:self.head_idx]
        print(f'_gen_new_data self.data{len(self.data)}')
        self._gen_new_idxs()

    def _open_hdf5(self):
        self._hf = h5py.File(self.file_path, 'r')

    def __getitem__(self, index) :
        # if not hasattr(self, '_hf'):
        #     self._open_hdf5()
        print(index)
        # x = self.file[self.datasets[0]][index]
        if index >= self.head_idx:
            self._gen_new_data()


        x = self.data[index]
        x = Image.fromarray(np.array(x))

        if self.transform:
            x = self.transform(x)
        else:
            x = torch.from_numpy(x)

        return x

    def __len__(self):
        return self.length

class MemHDF5Dataset(Data.Dataset):
    
    def __init__(self, file_path, datasets: tuple, transform=None, dataset_size=None):
        super().__init__()

        self.transform = transform
        self.length = dataset_size
        data = h5py.File(file_path, 'r')[datasets[0]][:dataset_size]
        self.data = []

        for i in range(0, self.length):
            x = data[i]
            x = Image.fromarray(np.array(x))
            
            if self.transform:
                x = self.transform(x)
            else:
                x = torch.from_numpy(x)

            self.data.append(x)

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return self.length
