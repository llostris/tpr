#!/usr/bin/env python

import math
import random
from mpi4py import MPI
from time import time
import sys
import numpy

__author__ = 'Magda'

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

random.seed(time() + rank)

TOTAL_POINTS = int(sys.argv[1])
POINTS = TOTAL_POINTS / size
R = 1

inside_circle = 0
pi = 0

comm.Barrier()
timer_start = MPI.Wtime()

for i in xrange(POINTS):
    x = random.uniform(-1, 1)
    y = random.uniform(-1, 1)

    if math.sqrt(x * x + y * y) < R:
        inside_circle += 1

data = comm.gather(inside_circle, root = 0)

if rank == 0:
    all_inside_circle = reduce(lambda x, y: x + y, data, 0) # replace with MPI reduce
    area = 4.0 * all_inside_circle / TOTAL_POINTS
    pi = area / (R * R)


comm.Barrier()
timer_end = MPI.Wtime()


if rank == 0:
    print 'parallel', TOTAL_POINTS, size, timer_end - timer_start, pi

MPI.Finalize()