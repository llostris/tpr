#!/usr/bin/env python

from mpi4py import MPI
from timer import Timer

__author__ = 'Magda'

TESTS = 100
ITERATIONS = 1

comm = MPI.COMM_WORLD
size = comm.Get_size()  # number of processes
rank = comm.Get_rank()
root_ID = 0

def print_result(result):
    print 'python barrier', size, result

timer = Timer(rank)
time = 0

for _ in xrange(TESTS):
    comm.Barrier()
    timer.start()
    comm.Barrier()
    timer.end()
    if rank == 0:
        time += timer.get_result()

if rank == 0:
    time = time * 1.0 / TESTS * 1e3     # miliseconds
    print_result(time)

# alternative implementation

# timer = Timer(rank, TESTS)
# time = 0
#
# timer.start()
# for _ in xrange(TESTS):
#     comm.Barrier()
# timer.end()
# if rank == 0:
#     print_result(timer.get_result() * 1e3)