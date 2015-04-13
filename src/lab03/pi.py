#!/usr/bin/env python

import math
import sys

__author__ = 'Magda'

import random
from mpi4py import MPI

POINTS = int(sys.argv[1]) #1000000000 # 1 mld
R = 1
inside_circle = 0

timer_start = MPI.Wtime()
for i in xrange(POINTS):
    x = random.uniform(-1, 1)
    y = random.uniform(-1, 1)

    if math.sqrt(x * x + y * y) <= R:
        inside_circle += 1

area = inside_circle * 1.0 / POINTS * 4
pi = area / (R * R)

timer_end = MPI.Wtime()
time = timer_end - timer_start
print 'normal', POINTS, 1, time, pi

MPI.Finalize()