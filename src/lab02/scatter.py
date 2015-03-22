#!/usr/bin/env python

from mpi4py import MPI
from timer import Timer
import sys
import numpy

__author__ = 'Magda'

TESTS = 100
ITERATIONS = 100

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
root_ID = 0


def usage_info():
    print 'Usage: ./scatter.py [package_size]'


def scatter(buffer, root = 0):
    if rank == root:
        index = 0
        for proc_id in xrange(1, size):
            comm.Send(buffer[index:index + 1], dest = proc_id)
            index += 1
        return buffer[root:root + 1]
    else:
        return comm.Recv(buffer, source = root)


def print_result(result_mpi, result_my):
    print 'python scatter', result_my, result_mpi

# read arguments

if len(sys.argv) < 2:
    usage_info()

package_size = int(sys.argv[1])

buffer = numpy.ndarray(shape=(size, package_size), dtype='b')
time_my = 0
time_mpi = 0
start_time = 0
end_time = 0

timer = Timer(rank, ITERATIONS)

comm.Barrier()

for _ in xrange(TESTS):

    # MPI implementation

    for i in xrange(ITERATIONS):
        timer.start()
        comm.scatter(buffer)
        comm.Barrier()    # wait until all complete
        timer.end()
        if rank == 0:
            time_mpi += timer.get_result()

    comm.Barrier()

    # my implementation

    for j in xrange(ITERATIONS):
        timer.start()
        scatter(buffer)
        comm.Barrier()    # wait until all complete
        timer.end()
        if rank == 0:
            time_my += timer.get_result()

if rank == 0:
    time_my = time_my / TESTS * 1e3
    time_mpi = time_mpi / TESTS * 1e3

    print_result(time_mpi, time_my)

MPI.Finalize()