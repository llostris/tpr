#!/usr/bin/env python

from mpi4py import MPI
from timer import Timer
import sys
import numpy

__author__ = 'Magda'

TESTS = 100
ITERATIONS = 100
BUFFER_SIZE = 10

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
root_ID = 0


def usage_info():
    print 'Usage: ./broadcast [group1_size] [group2_size]'


def broadcast(buffer):
    if rank == root_ID:
        for proc_id in xrange(1, size):
            comm.Send(buffer, dest = proc_id)
    else:
        comm.Recv(buffer, source = root_ID)


def print_result(result, result_my):
    print 'python broadcast', result_my, result

# read arguments

if len(sys.argv) < 2:
    usage_info()

group1_size = int(sys.argv[1])
group2_size = int(sys.argv[2])

buffer = numpy.arange(BUFFER_SIZE, dtype='b')
time_my_broadcast = 0
time_broadcast = 0
start_time = 0
end_time = 0

timer = Timer(rank, ITERATIONS)

comm.Barrier()

for _ in xrange(TESTS):

    # MPI implementation

    for i in xrange(ITERATIONS):
        timer.start()
        comm.bcast(buffer, root = root_ID)
        # comm.Barrier()    # wait until all complete
        timer.end()
        if rank == 0:
            time_broadcast += timer.get_result()

    comm.Barrier()
    # my implementation

    for j in xrange(ITERATIONS):
        timer.start()
        broadcast(buffer)
        # comm.Barrier()    # wait until all complete
        timer.end()
        if rank == 0:
            time_my_broadcast += timer.get_result()

if rank == 0:
    time_my_broadcast = time_my_broadcast / TESTS * 1e3
    time_broadcast = time_broadcast / TESTS

    print_result(time_broadcast, time_my_broadcast)

MPI.Finalize()