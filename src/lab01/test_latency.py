#!/usr/bin/env python

from mpi4py import MPI
import sys
import numpy

ITERATIONS = 1000
RUNS = 100
# comm_type = 'standard'

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

def usage_info():
    print 'Usage: ./test_comm.py [msg size] [standard/synchronous] [iterations per test] [number of tests]'
    print 'Two last arguments aren\'t required'
    sys.exit(-1)

def rankZeroStandard(buffer, buffer_size):
    for i in xrange(ITERATIONS):
        comm.Send(buffer[:buffer_size], dest = 1)
        comm.Recv(buffer[:buffer_size], source = 1)

def rankZeroSynchronous(buffer, buffer_size):
    for i in xrange(ITERATIONS):
        comm.Ssend(buffer[:buffer_size], dest = 1)
        comm.Recv(buffer[:buffer_size], source = 1)

def rankOne(buffer, buffer_size):
    for i in xrange(ITERATIONS):
        status = MPI.Status()
        comm.Recv(buffer[:buffer_size], source = 0, status = status)
        if comm_type == 'standard':
            comm.Send(buffer[:buffer_size], dest = 0)
        else:
            comm.Ssend(buffer[:buffer_size], dest = 0)

def save_result(result):
    with open('latency_python.txt', 'w') as file:
        file.write(str(result))

# main program

if len(sys.argv) < 2 :
    usage_info()

package_size = int(sys.argv[1])
comm_type = sys.argv[2]
if len(sys.argv) > 3 :
    ITERATIONS = int(sys.argv[3])
if len(sys.argv) > 4 :
    RUNS = int(sys.argv[4])
buffer = numpy.arange(package_size, dtype='b')

total_delay = 0

comm.Barrier()

for _ in xrange(RUNS):

    if rank == 0 :

        time_start = MPI.Wtime()

        if comm_type == 'standard' :
            rankZeroStandard(buffer, package_size)
        elif comm_type == 'synchronous' :
            rankZeroSynchronous(buffer, package_size)

        time_end = MPI.Wtime()

        # gather statistics
        time = time_end - time_start
        total_delay += time / (2 * ITERATIONS)

    elif rank == 1 :

        rankOne(buffer, package_size)

if rank == 0 :
    latency = total_delay / RUNS * 1e3  # in miliseconds
    print 'python latency', package_size, comm_type, latency