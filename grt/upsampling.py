import numpy as np

def data_upsampling(data,size):

    data = np.kron(data, np.ones(size))

    return data