import numpy as np
from functools import total_ordering
from heapq import heappop, heappush


def Knn(record, k, data, labels):
    """
    A modified version of K-nearest-neighbors for calculating the k-closest records to the given one.
    It is based ona min heap that always keeps the records with the minimum distance from the given
    record at the top, eliminating the need for sorting.

    :param record: (pandas.Series) The central record.
    :param k: (int) The number of neighbors to be calculated.
    :param data: (pandas.DataFrame) All the records.
    :param labels: (list) The cluster label of each 'data' record.
    :return: (int) The most frequent cluster label among the nearest records.
    """
    min_heap = []

    for element, label in zip(data, labels):

        dist = np.linalg.norm(record - element)
        if dist == 0:
            continue

        sample = Wrapper(label, dist)
        heappush(min_heap, sample)
        if len(min_heap) > k:
            heappop(min_heap)

    # The different labels and the number each of them appears in the heap.
    unique_vals, counts = np.unique([idx.index for idx in min_heap], return_counts=True)
    # The most frequent label in the heap.
    max_count_idx = np.argmax(counts)

    return unique_vals[max_count_idx]


@total_ordering
class Wrapper:
    """
    A wrapper class used in a minimum heap structure to keep the record labels with the minimum distance from a given
    point in ascending order at the top of the heap.
    """
    def __init__(self, index, dist):
        """
        Initializing class variables.

        :param index: (int)The record's label.
        :param dist: (float)The Euclidean distance from the central record.
        """
        self.index = index
        self.dist = dist

    def __lt__(self, other):
        """
        Overriding the heap 'larger than' comparator.
        """
        return self.dist > other.dist
