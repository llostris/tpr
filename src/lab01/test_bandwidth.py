#!/usr/bin/env python

from mpi4py import MPI
import sys
import numpy

TESTS = 100
ITERATIONS = 10000
BANDWIDTH_FACTOR = 8.0 / (1024 * 1024)
STEP = 1000

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

def usage_info():
    print 'Usage: ./test_comm.py [max size] [standard/synchronous] [tests] [step size]'
    print 'Requirements: Step size < max size'
    sys.exit(-1)

def sendMessageStandard(buffer, buffer_size):
    for i in xrange(ITERATIONS / buffer_size):  # scale the number of iterations s
        comm.Send(buffer[:buffer_size], dest = 1)
        comm.Recv(buffer[:buffer_size], source = 1)

def sendMessageSynchronized(buffer, buffer_size):
    for i in xrange(ITERATIONS / buffer_size):
        comm.Ssend(buffer[:buffer_size], dest = 1)
        comm.Recv(buffer[:buffer_size], source = 1)

def receiveMessages(buffer, buffer_size):
    for i in xrange(ITERATIONS / buffer_size):
        status = MPI.Status()
        comm.Recv(buffer[:buffer_size], source = 0, status = status)
        if comm_type == 'standard':
            comm.Send(buffer[:buffer_size], dest = 0)
        else:
            comm.Ssend(buffer[:buffer_size], dest = 0)

def print_results(results):
    print 'bandwidth python', package_size, comm_type, ITERATIONS, TESTS
    size = STEP
    for result in results:
        print size, result
        size += STEP

# main program

if len(sys.argv) < 3 :
    usage_info()

package_size = int(sys.argv[1]) + 1
comm_type = sys.argv[2]
ITERATIONS = package_size
if len(sys.argv) > 3 :
    TESTS = int(sys.argv[3])
if len(sys.argv) > 4 :
    STEP = int(sys.argv[4])

buffer = numpy.arange(package_size, dtype='b')
bandwidth_sum = {}
for i in xrange(STEP, package_size, STEP):
    bandwidth_sum[i] = 0

comm.Barrier()

for _ in xrange(TESTS):

    for size in xrange(STEP, package_size, STEP):

        if rank == 0 :

            time_start = MPI.Wtime()

            if comm_type == 'standard' :
                sendMessageStandard(buffer, size)
            elif comm_type == 'synchronous' :
                sendMessageSynchronized(buffer, size)

            time_end = MPI.Wtime()

            # gather statistics
            time = time_end - time_start
            try:
                bandwidth = ITERATIONS * 1.0 / time
                bandwidth *= 2
                bandwidth_sum[size] += bandwidth * BANDWIDTH_FACTOR
            except ZeroDivisionError:
                pass

        elif rank == 1 :

            receiveMessages(buffer, size)

        else :
            print "Expected only two nodes"

if rank == 0:
    bandwidth_to_size = []
    for size in xrange(STEP, package_size, STEP):
        bandwidth_to_size.append(bandwidth_sum[size] / TESTS)
    print_results(bandwidth_to_size)

MPI.Finalize()