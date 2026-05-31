import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
# Load the iris dataset
iris = load_iris()
data = iris.data  # Numpy array
feature_names = iris.feature_names

# Convert to DataFrame for reference
df = pd.DataFrame(data, columns=feature_names)
print("First 5 rows of Iris Dataset:\n", df.head())

# a) Array dimensional, shape, and size
print("\n[a] Dimensional:", df.ndim)
print("Shape:", df.shape)
print("Size:", df.size)

# b) Array Slicing
print("\n[b] Slicing - First 5 rows:\n", df[:5])

# c) Array Indexing: Accessing Single Elements
print("\n[c] Element at [0, 0]:", data[0, 0])

# d) Array Slicing - Subarrays
# i. One-dimensional subarray
print("\n[d-i] One-dimensional (Row 0):", data[0])

# ii. Multidimensional subarray
print("\n[d-ii] First 3 rows, first 2 columns:\n", data[:3, :2])

# iii. Accessing array rows and columns
print("\n[d-iii] Second row:\n", data[1])
print("Third column of all rows:\n", data[:, 2])

# e) Creating copies of arrays
data_copy = data.copy()
data_copy[0, 0] = 999.9
print("\n[e] Original value:", data[0, 0])
print("Copied modified value:", data_copy[0, 0])

# f) Reshaping of Arrays
print("size",data[:12].size)


reshaped = data[:12].reshape(12,4)  # Reshape first 12 rows
print("\n[f] Reshaped (6x8) array:\n", reshaped)

# g) Array Concatenation and Splitting
# Concatenate two parts
part1 = data[:5]
part2 = data[5:10]
print(part2)
concatenated = np.concatenate((part1, part2), axis=0)
print("\n[g] Concatenated Array (first 10 rows):\n", concatenated)

# Splitting array into 3 parts
split_arrays = np.array_split(data[:15], 3  )
print("\nSplit into 3 parts:")
for i, arr in enumerate(split_arrays):
    print(f" Part {i+1}:\n", arr)