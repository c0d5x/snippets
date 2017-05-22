#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file has snippets for data analysis, numpy, pandas, etc.
"""


import math
import numpy as np


list10ints = range(10)

# Map
print("Maps:")
list10floats = map(float, list10ints)
print(list10floats)
print(map(math.sqrt, list10floats))


# Filter
print("Filters:")


def div_2(num):
    return num % 2 == 0

print("filter test div_2(2) ", div_2(2))
print("filter test div_2(1) ", div_2(1))
print(map(div_2, list10ints))
filtered10 = filter(div_2, list10ints)
print("filtered list: ", filtered10)

# List comprehensions
print("List comprehensions:")
print([x**3 for x in filtered10])
print([x**3 for x in list10ints if x % 2 == 0])
print([float(x**3) for x in list10ints if x % 2 == 0])

# Lambda
print("Lambda:")
print(map(lambda x: float(x**3), list10ints))
print(map(lambda x: float(x**3), filter(lambda z: z % 2 == 0, list10ints)))


# NumPy
print("NumPy: ", np.__version__)
npa = np.arange(20)
npa = np.array([float(x**3) for x in list10ints if x % 2 == 0])
npa = np.linspace(1, 38, 5)
npa = np.random.random_integers(0, 50, 20)
print(npa.mean())
print(npa.std())
print(npa.sum())
print(npa.max())
print(npa.min())
print(npa ** 3)
npa = np.arange(20)
print(npa[npa % 2 == 0])
print(npa[npa > 10])
print(npa.dtype)
print(npa.shape)
print(np.linspace(1, 38, 5))


def single_arg_func(arg):
    if arg < 10:
        return arg**2
    else:
        return arg**3

vectorized_func = np.vectorize(single_arg_func)
print(vectorized_func(npa))

npa = np.arange(25)
npa = npa.reshape((5, 5))
print(npa)
print(npa.transpose())
print(npa.flatten())
print(npa.cumsum())
