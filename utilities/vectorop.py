"""Utility functions that use the NumPy library"""
import warnings

import numpy as np


def upscale(A, mini, maxi):
    return A * (maxi - mini) + mini


def downscale(A, mini, maxi):
    return (A - mini) / (maxi - mini)


def rescale(X: np.ndarray, axis=0, ufctr=(0, 1), dfctr=None, return_factors=False):
    if X.ndim != 2:
        raise RuntimeError("Can only feature scale matrices!")
    dfctr = (X.min(axis=axis), X.max(axis=axis)) if dfctr is None else dfctr
    output = upscale(downscale(X, *dfctr), *ufctr)
    return (output, dfctr, ufctr) if return_factors else output


def standardize(X, mean=None, std=None, return_factors=False):
    mean = X.mean(axis=0) if mean is None else mean
    std = (X.std(axis=0) + 1e-8) if std is None else std
    scaled = (X - mean) / std
    return (scaled, (mean, std)) if return_factors else scaled


def euclidean(itr: np.ndarray, target: np.ndarray):
    # return np.linalg.norm(itr - target, axis=0)  slower !!!
    return np.sqrt(np.sum(np.square(itr - target), axis=0))


def ravel_to_matrix(A):
    A = np.atleast_2d(A)
    return A.reshape(A.shape[0], np.prod(A.shape[1:]))


def argshuffle(array):
    indices = np.arange(len(array))
    np.random.shuffle(indices)
    return indices


def shuffle(*arrays):
    indices = argshuffle(arrays[0])
    return tuple(map(lambda ar: ar[indices], arrays))


def dummycode(dependent, get_translator=True):
    categ = np.unique(dependent)
    dummy = np.arange(len(categ))

    dummy_dict = dict()
    dreverse = dict()

    applier = np.vectorize(lambda x: dummy_dict[x])
    reverter = np.vectorize(lambda x: dreverse[x])

    for c, d in zip(categ, dummy):
        dummy_dict[d] = c
        dummy_dict[c] = d

    dependent = applier(dependent)
    return (dependent, applier, reverter) if get_translator else dependent


def split_by_categories(labels: np.ndarray, X: np.ndarray=None):
    categ = np.unique(labels)
    argsbycat = {cat: np.argwhere(labels == cat).ravel() for cat in categ}
    return argsbycat if X is None else {cat: X[argsbycat[cat]] for cat in categ}


def separate_validation(ratio, X, Y, balanced=False, nowarning=False):

    def simple_separate(alpha, array, array2=None):
        N = len(array)
        m = int(N * alpha)
        arg = np.arange(N)
        varg, larg = arg[:m], arg[m:]
        lX, vX = array[larg], array[varg]
        return (lX, vX) if array2 is None else (lX, array2[larg], vX, array2[varg])

    def balanced_separate(alpha, array, array2):
        cat_arg = split_by_categories(array2)
        lX, lY, vX, vY = [], [], [], []
        for cat, arg in cat_arg.items():
            larg, varg = simple_separate(alpha, arg)
            if len(varg) == 0 and not nowarning:
                warnings.warn(f"Too few samples in {cat} to separate with ratio {alpha:.2%}! Skipping!")
                continue
            lX.append(array[larg])
            lY.append(array2[larg])
            vX.append(array[varg])
            vY.append(array2[varg])
        return list(map(np.concatenate, (lX, lY, vX, vY)))

    return (balanced_separate if balanced else simple_separate)(ratio, X, Y)
