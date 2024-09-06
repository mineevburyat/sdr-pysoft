import numpy as np
 
def n_largest_indices(arr, n):
    return np.argpartition(arr, -n)[-n:]
 
array = np.array([1, 3, 2, 4, 5, 0, 6, 8])
n = 5
print(n_largest_indices(array, n))

def n_largest_indices_sorted(arr, n):
    indices = np.argpartition(arr, -n)[-n:]
    return indices[np.argsort(-arr[indices])]
 
print(n_largest_indices_sorted(array, n))
db_12video_chan = [item * 10* 1000000 for item in range(96, 154, 4)]
print(db_12video_chan)