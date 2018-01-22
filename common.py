#coding=utf-8
import uniout
import numpy as np
from random import randint
import pandas as pd

def readdata(filename):
    '''
    :param filename: file path
    :return: numpy.ndarray of the data split by '\t' and '\n'
    '''
    f = file(filename,'r')
    ret = []
    for line in open(filename):
        line = f.readline().rstrip(u'\n')
        ret.append(line.split(u'\t'))
    ret = np.array(ret)
    return ret

def readtable(filename):
    data = readdata(filename)
    return pd.DataFrame(data[1:-1],columns=data[0])

def random_nodup(numlist):
    index = randint(0,numlist.__len__()-1)
    num = numlist[index]
    numlist.remove(num)
    return num
