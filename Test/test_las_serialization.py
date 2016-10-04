import json

import lasio
import pickle

mode = 9

if __name__ == '__main__':
    if mode == 0:
        las = lasio.read('/home/danila/PycharmProjects/gazprom/gazprom_new/data/las/805.las')
        f = open('las_file1', 'wb')
        pickle.dump(las, f)
    else:
        f = open('las_file1', 'rb')
        l = pickle.load(f)
        print(l.get_curve('GR'))
