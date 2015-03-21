#!/usr/bin/env python

from mpi4py import MPI

class Timer:

    def __init__(self, rank, iterations = 1):
        self.time_start = 0
        self.time_end = 0
        self.rank = rank
        self.iterations = iterations

    def start(self):
        self.time_start = MPI.Wtime()

    def end(self):
        self.time_end = MPI.Wtime()

    def get_result(self):
        return (self.time_end - self.time_start) * 1.0 / self.iterations
