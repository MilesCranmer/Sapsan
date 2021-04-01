"""
HDF5 dataset classes

Usage:
    data_loader = HDF5Dataset(path="/path/to/data.h5",
                      features=['a', 'b'],
                      target=['c'],
                      checkpoints=[0.0, 0.01],
                      batch_size=BATCH_SIZE,
                      input_size=INPUT_SIZE,
                      sampler=sampler,
                      flat = False)

    x, y = data_loader.load_numpy()
"""

from typing import List, Tuple, Dict, Optional
import numpy as np
import h5py as h5

from sapsan.core.models import Dataset, Sampling
from sapsan.utils.shapes import split_cube_by_batch, split_square_by_batch
from .data_functions import torch_splitter, flatten

class HDF5Dataset(Dataset):
    def __init__(self,
                 path: str,
                 checkpoints: List[int],
                 input_size,
                 features: List[str],
                 target = None,
                 batch_size: int = None,
                 sampler: Optional[Sampling] = None,
                 time_granularity: float = 1,
                 features_label: Optional[List[str]] = None,
                 target_label: Optional[List[str]] = None,
                 flat: bool = False,
                 shuffle: bool = False,
                 train_fraction = None):

        """
        @param path:
        @param features:
        @param target:
        @param checkpoints:
        @param batch_size: size of cube that will be used to separate checkpoint data
        """
        self.path = path
        self.features = features
        self.target = target
        self.features_label = features_label
        self.target_label = target_label
        self.checkpoints = checkpoints
        self.batch_size = batch_size
        self.sampler = sampler
        self.input_size = input_size
        self.initial_size = input_size
        self.axis = len(self.input_size)
        self.flat = flat
        self.shuffle = shuffle
        self.train_fraction = train_fraction

        if sampler:
            self.input_size = self.sampler.sample_dim
        if batch_size==None: self.num_batches = 1
        else: self.num_batches = int(np.prod(np.array(self.input_size))/np.prod(np.array(self.batch_size)))
        self.time_granularity = time_granularity
    
    def get_parameters(self):
        parameters = {
            "data - path": self.path,
            "data - features": str(self.features)[1:-1].replace("'",""),
            "data - target": str(self.target)[1:-1].replace("'",""),
            "data - features_label": self.features_label,
            "data - target_label": self.target_label,
            "data - axis": self.axis,
            "data - shuffle": self.shuffle,
            "chkpnt - time": self.checkpoints,
            "chkpnt - initial size": self.initial_size,
            "chkpnt - sample to size": self.input_size,
            "chkpnt - time_granularity": self.time_granularity,
            "chkpnt - batch_size": self.batch_size,
            "chkpnt - num_batches" : self.num_batches
        }
        return parameters
    
    
    def load_numpy(self) -> Tuple[np.ndarray, np.ndarray]:
        #return loaded data as a numpy array only
        return self._load_data_numpy()
    
    def convert_to_torch(self, loaders: np.ndarray):
        #split into batches and convert numpy to torch dataloader
        loaders = torch_splitter(loaders[0], loaders[1], 
                                 num_batches = self.num_batches, 
                                 train_fraction = self.train_fraction,
                                 shuffle = self.shuffle)
        return loaders
    
    def load(self):
        #load numpy, split into batches, convert to torch dataloader, and return it        
        loaders = self.load_numpy()
        return self.convert_to_torch(loaders)                
    
        
    def split_batch(self, input_data):
        # columns_length ex: 12 features * 3 dim = 36  
        columns_length = input_data.shape[0]
        if self.axis == 3:
            return split_cube_by_batch(input_data, self.input_size,
                                      self.batch_size, columns_length)
        if self.axis == 2:
            return split_square_by_batch(input_data, self.input_size,
                                      self.batch_size, columns_length)
    
    def _get_path(self, checkpoint, feature):
        """Return absolute path to required feature at specific checkpoint."""
        timestep = self.time_granularity * checkpoint
        relative_path = self.path.format(checkpoint=timestep, feature=feature)
        return relative_path

    
    def _get_input_data(self, checkpoint, columns, labels):
        all_data = []
        # combine all features into cube with channels
                
        for col in range(len(columns)):
            file = h5.File(self._get_path(checkpoint, columns[col]), 'r')
            
            if labels==None: key = list(file.keys())[-1]
            else: key = label[col]

            print("Loading '%s' from file '%s'"%(key, self._get_path(checkpoint, columns[col])))
            
            data = file.get(key)
            
            if (self.axis==3 and len(np.shape(data))==3) or (self.axis==2 and len(np.shape(data))==2): 
                data = [data]     
            all_data.append(data)
            
        # input_data shape ex: (features, 128, 128, 128)        
        input_data = np.vstack(all_data)

        # downsample if needed
        if self.sampler:
            input_data = self.sampler.sample(input_data)
                
        if self.flat: return flatten(input_data)
        elif self.batch_size == self.input_size: return input_data
        else: return self.split_batch(input_data)


    def _load_data_numpy(self) -> Tuple[np.ndarray, np.ndarray]:
        x = list()
        y = list()
        for checkpoint in self.checkpoints:
            features_checkpoint_batch = self._get_input_data(checkpoint, 
                                                                  self.features, self.features_label)
            x.append(features_checkpoint_batch)
            x = np.vstack(x)
            print('Loaded INPUT data shape', x.shape)
            
            loaded_data = x
            
            if self.target!=None:
                target_checkpoint_batch = self._get_input_data(checkpoint, 
                                                                    self.target, self.target_label)
                y.append(target_checkpoint_batch)
                y = np.vstack(y)                        
                print('Loaded TARGET data shape', y.shape)
                
                loaded_data = np.array([loaded_data, y])
                
        return loaded_data
