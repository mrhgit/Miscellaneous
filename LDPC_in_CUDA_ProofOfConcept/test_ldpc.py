#!/usr/bin/python3

import numpy as np

H = np.asarray([[1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 1, 0, 0, 0, 1, 1],
                [1, 0, 1, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, 0, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 1, 1, 1]])

sent = np.asarray([1, 0, 1, 0, 1, 1, 1, 0, 1, 0])
recv = np.asarray([1, 0, 1, 0, 1, 1, 1, 0, 1, 1])

sent_syndromes = np.matmul(H,sent) % 2
recv_syndromes = np.matmul(H,recv) % 2

print(sent_syndromes)
print(recv_syndromes)

