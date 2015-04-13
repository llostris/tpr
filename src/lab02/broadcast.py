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
    print 'Usage: ./broadcast.py [buffer_size]'


def broadcast(buffer, root = root_ID):
    if rank == root:
        for proc_id in xrange(1, size):
            comm.Send(buffer, dest = proc_id)
        return buffer
    else:
        return comm.Recv(buffer, source = root)


def print_result(result, result_my):
    print 'python broadcast', result_my, result

# read arguments

if len(sys.argv) < 2:
    usage_info()

BUFFER_SIZE = int(sys.argv[1])

buffer = numpy.arange(BUFFER_SIZE, dtype='b')
time_my = 0
time_mpi = 0
start_time = 0
end_time = 0

timer = Timer(rank, ITERATIONS)

comm.Barrier()

for _ in xrange(TESTS):

    # MPI implementation

    timer.start()
    for i in xrange(ITERATIONS):
        comm.bcast(buffer, root = root_ID)
        comm.Barrier()    # wait until all complete
        timer.end()
    if rank == 0:
        time_mpi += timer.get_result()

    comm.Barrier()

    # my implementation

    timer.start()
    for j in xrange(ITERATIONS):
        broadcast(buffer)
        comm.Barrier()    # wait until all complete
    timer.end()
    if rank == 0:
        time_my += timer.get_result()

if rank == 0:
    time_my = time_my / TESTS * 1e3
    time_mpi = time_mpi / TESTS * 1e3

    print_result(time_mpi, time_my)

MPI.Finalize()