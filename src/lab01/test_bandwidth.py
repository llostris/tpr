#!/usr/bin/env python

from mpi4py import MPI
import sys
import numpy

TESTS = 100
ITERATIONS = 1000
BANDWIDTH_FACTOR = 8.0 / (1024 * 1024)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

def usage_info():
    print 'Usage: ./test_comm.py [max size] [standard/synchronous] [iterations] [tests]'
    sys.exit(-1)

def sendMessageStandard(buffer, buffer_size):
    for i in xrange(ITERATIONS):  # scale the number of iterations s
        comm.Send(buffer[:buffer_size], dest = 1)
        comm.Recv(buffer[:buffer_size], source = 1)

def sendMessageSynchronized(buffer, buffer_size):
    for i in xrange(ITERATIONS):
        comm.Ssend(buffer[:buffer_size], dest = 1)
        comm.Recv(buffer[:buffer_size], source = 1)

def receiveMessages(buffer, buffer_size):
    for i in xrange(ITERATIONS):
        status = MPI.Status()
        comm.Recv(buffer[:buffer_size], source = 0, status = status)
        if comm_type == 'standard':
            comm.Send(buffer[:buffer_size], dest = 0)
        else:
            comm.Ssend(buffer[:buffer_size], dest = 0)

def print_results(result):
    print 'python bandwidth', package_size, comm_type, result

# main program

if len(sys.argv) < 3 :
    usage_info()

package_size = int(sys.argv[1])
comm_type = sys.argv[2]
if comm_type != 'standard' and comm_type != 'synchronous':
    usage_info()

buffer = numpy.arange(package_size, dtype='b')
if len(sys.argv) > 3 :
    ITERATIONS = int(sys.argv[3])
if len(sys.argv) > 4 :
    TESTS = int(sys.argv[4])

bandwidth_sum = 0

comm.Barrier()

for _ in xrange(TESTS):

    if rank == 0 :

        time_start = MPI.Wtime()

        if comm_type == 'standard' :
            sendMessageStandard(buffer, package_size)
        elif comm_type == 'synchronous' :
            sendMessageSynchronized(buffer, package_size)

        time_end = MPI.Wtime()

        # gather statistics
        time = time_end - time_start
        try:
            bandwidth = ITERATIONS * package_size * 1.0 / time
            bandwidth *= 2
            bandwidth_sum += bandwidth * BANDWIDTH_FACTOR
        except ZeroDivisionError:
            pass

    elif rank == 1 :

        receiveMessages(buffer, package_size)

if rank == 0:
    print_results(bandwidth_sum / TESTS)

MPI.Finalize()