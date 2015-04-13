__author__ = 'Magda'
from matplotlib import pyplot as plt

datafile = 'results/bandwidth_1core_'
datafile = 'results/bandwidth_2node_'
# datafile = 'bandwidth_'

modes = [ 'standard', 'synchronous' ]
handles = []
for mode in modes:
    print mode
    data_x = [] # read data
    data_y  = []

    with open(datafile + mode + '.txt') as f:
        all_data = f.readlines()
        for line in all_data[1:]:
            data = line.split()
            data_x.append(int(data[0]))
            data_y.append(float(data[1]))
            print(float(data[1]))
        f.close()

    lines, = plt.plot(data_x, data_y, label=mode)
    handles.append(lines)
    plt.suptitle('Bandwidth')
    plt.ylabel('bandwidth [Mb/s]')
    plt.xlabel('message size [B]')
    for x in data_x:
        print x

print
plt.legend(handles, ['Standard', 'Synchronized'])
plt.savefig(datafile + '.png')