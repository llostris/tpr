__author__ = 'Magda'

from matplotlib import pyplot as plt

datafile = 'results.txt'
PLOT_DIRECTORY = 'results/'


# normal/parallel, points, nodes, time, pi
types = [ 'normal', 'parallel']
points = [ 1000000, 10000000, 100000000 ]
sequential_time = {}

def speedup(time_old, time_new):
    return time_old / time_new


def efficiency(speedup, processes):
    return speedup / processes


def karp_flatt(speedup, processes):
    inv_processes = 1.0 / processes
    numerator = 1.0 / speedup - inv_processes
    return numerator / (1 - inv_processes)


def get_column(array, index):
    column = []
    for row in array:
        column.append(row[index])
    return column

def sort_plotted_data(x, y):
    return sorted(zip(x, y), key=lambda x: x[0])

##### plotting functions

def plot_time_regular(data):
    plt.clf()
    handles = []
    for type in types:
        data = filter(lambda x: x[0] == type, data)
        if len(data) > 0:
            lines, = plt.plot(get_column(data, 1), get_column(data, 3))
            handles.append(lines)
            plt.suptitle('Plot of time in function of number of points')
            plt.ylabel('Time [s]')
            plt.xlabel('Number of points')
            plt.legend(handles, types)
            plt.savefig('time_regular.png')
            for i in zip(get_column(data, 1), get_column(data, 3)):
                sequential_time[i[0]] = i[1]


def plot_time_parallel(data, prefix):
    plt.clf()
    handles = []
    legend = []
    for type in sorted(set(get_column(data, 2))):
        filtered = filter(lambda x: x[2] == type, data)
        # print type, filtered
        if len(filtered) > 0:
            xy = sort_plotted_data(get_column(filtered, 1), get_column(filtered, 3))
            lines, = plt.plot(get_column(xy, 0), get_column(xy, 1))
            handles.append(lines)
            legend.append('nodes=' + str(type))
    plt.suptitle('Plot of time in function of number of points')
    plt.ylabel('Time [s]')
    plt.xlabel('Number of points')
    # print handles, legend
    plt.legend(handles, legend)
    plt.savefig(prefix + '-time-parallel.png')


def plot_time_processes(data, prefix):
    plt.clf()
    handles = []
    legend = []
    for size in sorted(set(get_column(data, 1))):
        filtered = filter(lambda x: x[1] == size, data)
        if len(filtered) > 0:
            xy = sort_plotted_data(get_column(filtered, 2), get_column(filtered, 3))
            lines, = plt.plot(get_column(xy, 0), get_column(xy, 1))
            handles.append(lines)
            legend.append('points=' + str(size))
    plt.suptitle('Plot of time in function of number of processes')
    plt.ylabel('Time [s]')
    plt.xlabel('Processes')
    plt.legend(handles, legend)
    plt.savefig(prefix + '-time-processes.png')


def make_plot(x, y, title, xlabel, ylabel, filename):
    plt.clf()
    handles = []
    legend = []
    lines, = plt.plot(x, y)
    handles.append(lines)

    plt.suptitle(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.legend(handles, legend)
    plt.savefig(filename)


def plot_metrics(data, prefix):
    for size in points:
        data_speedup = []
        data_efficiency = []
        data_karp = []
        filtered_size = filter(lambda x: x[1] == size, data)
        if len(filtered_size) > 0:
            filtered = sort_plotted_data(get_column(filtered_size, 2), get_column(filtered_size, 3))
            nodes = get_column(filtered, 0)
            times = get_column(filtered, 1)
            # print nodes, times

            time_old = times[0]
            time_old = sequential_time[size]
            for time_new in times[1:]:
                data_speedup.append(speedup(time_old, time_new))

            for sp in zip(data_speedup, nodes[1:]):
                data_efficiency.append(efficiency(sp[0], sp[1]))
                data_karp.append(karp_flatt(sp[0], sp[1]))
            # print len(data_speedup), len(nodes[1:]), len(data_efficiency), len(data_karp)

            make_plot(nodes[1:], data_speedup,
                      title='Speedup in function of processes for points = ' + str(size),
                      xlabel='Processes', ylabel='Speedup',
                      filename=prefix + '-speedup-' + str(size) + '.png')

            make_plot(nodes[1:], data_efficiency,
                      title='Efficiency in function of processes for points = ' + str(size),
                      xlabel='Processes', ylabel='Efficiency',
                      filename=prefix + '-efficiency-' + str(size) + '.png')

            make_plot(nodes[1:], data_karp,
                      title='Karp-Flatt metric in function of processes for points = ' + str(size),
                      xlabel='Processes', ylabel='Karp-Flatt metric',
                      filename=prefix + '-karp-' + str(size) + '.png')


def load_data(datafile):
    data = []
    with open(datafile) as f :
        for line in f.readlines():
            if len(line.strip()) > 0:
                splitted = line.split()
                arr = [ splitted[0], int(splitted[1]), int(splitted[2]), float(splitted[3]), float(splitted[4]) ]
                # first data format: type, pi, points, time, nodes -> remap
                # arr = [ splitted[0], int(splitted[2]), int(splitted[4]), float(splitted[3]), float(splitted[1]) ]
                data.append(arr)
        f.close()
    return data

def fix_scaled_times(data):
    for line in data:
        line[3] = line[3] / line[2]

######## MAIN PROGRAM

if __name__ == "__main__":

    data = load_data(datafile)
    # create plots

    plot_time_regular(data)
    print sequential_time

    # regular
    data_parallel = filter(lambda x: x[0] == 'parallel', data)
    plot_time_parallel(data_parallel, 'reg')
    plot_time_processes(data_parallel, 'reg')
    plot_metrics(data_parallel, 'reg')

    # scaled
    data_scaled = load_data('results-scaled2.txt')
    for line in data_scaled:
        line[1] = line[1] / line[2]
    # print data_scaled
    plot_time_parallel(data_scaled, 'scaled')
    plot_time_processes(data_scaled, 'scaled')
    fix_scaled_times(data_scaled)
    plot_metrics(data_scaled, 'scaled')