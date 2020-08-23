import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from rich.console import Console
from rich.table import Table
from functools import partial
import sys
import os
from pathlib import Path
sys.path.append(str(Path(os.path.abspath(__file__)).parent.parent))
from utils import *

class KDTree:
    class Node:
        def __init__(self, points, labels, axis):
            self.points = points
            self.labels = labels
            self.axis = axis
            self.left = None
            self.right = None

    def build(self, X, Y, split_axis=0):
        if not len(X):
            return None
        median_ind = np.argpartition(X[:, split_axis], len(X) // 2, axis=0)[-1]
        split_point = float(X[median_ind, split_axis])
        equal_x = X[X[:, split_axis] == split_point]
        equal_y = Y[X[:, split_axis] == split_point]
        less_x = X[X[:, split_axis] < split_point]
        less_y = Y[X[:, split_axis] < split_point]
        greater_x = X[X[:, split_axis] > split_point]
        greater_y = Y[X[:, split_axis] > split_point]
        node = self.Node(equal_x, equal_y, split_axis)
        node.left = self.build(less_x, less_y, 1 - split_axis)
        node.right = self.build(greater_x, greater_y, 1 - split_axis)
        return node

    def _query(self, root, x, k):
        if not root:
            return Heap(max_len=k, key=lambda xy: -euc_dis(x, xy[0])), inf
        mindis = inf
        # Find the region that contains the target point
        if x[root.axis] <= root.points[0][root.axis]:
            ans, lmindis = self._query(root.left, x, k)
            mindis = min(mindis, lmindis)
            sibling = root.right
        else:
            ans, rmindis = self._query(root.right, x, k)
            mindis = min(mindis, rmindis)
            sibling = root.left
        # All the points on the current splitting line are possible answers
        for curx, cury in zip(root.points, root.labels):
            mindis = min(euc_dis(curx, x), mindis)
            ans.push((curx, cury))
        # If the distance between the target point and the splitting line is
        # shorter than the best answer up until, find the other tree
        if mindis > abs(x[root.axis] - root.points[0][root.axis]):
            other_ans, other_mindis = self._query(sibling, x, k)
            mindis = min(mindis, other_mindis)
            while other_ans:
                otherx, othery = other_ans.pop()
                ans.push((otherx, othery))
        return ans, mindis

    def query(self, x, k):
        return self._query(self.root, x, k)[0]

    def __init__(self, X, Y):
        self.root = self.build(X, Y)

class KNN:
    def __init__(self, k=1, distance_func="l2"):
        self.k = k
        if distance_func == 'l2':
            self.distance_func = lambda x, y: np.linalg.norm(x - y)
        else:
            self.distance_func = distance_func

    def _predict(self, x):
        topk = self.tree.query(x, self.k)
        topk_y = [y for x, y in topk]
        return np.argmax(np.bincount(topk_y))

    def fit(self, X, Y):
        self.tree = KDTree(X, Y)
        self.k = min(self.k, len(X))

    def predict(self, X):
        return np.apply_along_axis(self._predict, axis=-1, arr=X)

if __name__ == "__main__":
    console = Console(markup=False)
    # -------------------------- Example 1 ----------------------------------------
    print("Example 1:")
    knn = KNN()
    X_train = np.array([[0, 0], [0, 1], [1, 0], [1, 1], [.5, .5]])
    Y_train = np.array([1, 2, 3, 4, 5])
    knn.fit(X_train, Y_train)
    # generate grid-shaped test data
    X_test = np.concatenate(np.stack(np.meshgrid(np.linspace(-1, 2, 100), np.linspace(-1, 2, 100)), axis=-1))
    # X_test = X_train
    pred_test = knn.predict(X_test)

    # plot
    plt.scatter(X_test[:,0], X_test[:,1], c=pred_test, marker=".", s=1)
    plt.show()

    # -------------------------- Example 2 (Imblance Data) ------------------------
    print("Example 2:")
    X_train = np.array([[0, 0], [0, 1], [1, 0], [1, 1], [.5, .5]])
    Y_train = np.array([1, 1, 2, 3, 4])
    knn = KNN(k=2)
    knn.fit(X_train, Y_train)
    # generate grid-shaped test data
    X_test = np.concatenate(np.stack(np.meshgrid(np.linspace(-1, 2, 100), np.linspace(-1, 2, 100)), axis=-1))
    # X_test = X_train
    pred_test = knn.predict(X_test)

    # plot
    plt.scatter(X_test[:,0], X_test[:,1], c=pred_test, marker=".", s=1)
    plt.show()