import numpy as np
from skimage.util import view_as_blocks
from logging import warning
from typing import List, Tuple, Dict, Optional

def split_cube_by_batch(data: np.ndarray,
                        input_size: tuple,
                        batch_size: tuple,
                        n_features: int) -> np.ndarray:
    """ --3D-- Splits big cube into smaller ones into batches.

    @param data: (channels, batch_size, batch_size, batch_size)
    @return (batch, channels, batch_size, batch_size, batch_size)
    """    
    batch = int(np.prod(input_size) / np.prod(batch_size))
    return view_as_blocks(data, block_shape=(n_features, batch_size[0],
                                             batch_size[1], batch_size[2])
                          ).reshape(batch, n_features,
                                    batch_size[0], batch_size[1], batch_size[2])

def split_square_by_batch(data: np.ndarray,
                       input_size: tuple,
                       batch_size: tuple,
                       n_features: int) -> np.ndarray:
    """ --2D-- Splits big square into smaller ones into batches.

    @param data: (channels, batch_size, batch_size)
    @return (batch, channels, batch_size, batch_size)
    """
    batch = int(np.prod(input_size) / np.prod(batch_size))
    return view_as_blocks(data, block_shape=(n_features, batch_size[0],
                                                 batch_size[1])
                          ).reshape(batch, n_features,
                                    batch_size[0], batch_size[1])


def combine_cubes(cubes: np.ndarray,
                  input_size: tuple,
                  batch_size: tuple) -> np.ndarray:
    """ Combines batches into one big cube.

    Reverse of split_cube_by_batch function.
    @param cubes: (batch, channels, batch_size, batch_size, batch_size)
    """    
    n_per_dim = np.empty(3, dtype=int)
    for i in range(3):
        n_per_dim[i] = int(input_size[i] / batch_size[i])
    x = []    
    for i in range(n_per_dim[0]):
        y = []
        for j in range(n_per_dim[1]):
            z = []
            for k in range(n_per_dim[2]):
                z.append(cubes[i * n_per_dim[0] * n_per_dim[1] + j * n_per_dim[2] + k])
            y.append(np.concatenate(z, axis=3))
        x.append(np.concatenate(y, axis=2))
    return np.concatenate(x, axis=1)


def slice_of_cube(data: np.ndarray,
                  feature: Optional[int] = None,
                  n_slice: Optional[int] = None):
    """ Slice of 3d cube

    @param data: numpy array
    @param feature: feature of cube to use in case of multifeature plot
    @param n_slice: slice to use
    @return: pyplot object
    """
    if len(data.shape) not in [3, 4]:
        return None

    if len(data.shape) == 4:
        if feature is None:
            warning("Feature was not provided. First one will be used")
            feature = 0
        data = data[feature, :, :, :]

    if n_slice is None:
        warning("Slice is not selected first one will be used")
        n_slice = 0

    slice_to_plot = data[n_slice]

    return slice_to_plot