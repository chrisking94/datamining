#coding=utf-8
import uniout
import numpy as np
from random import randint
import pandas as pd

def readdata(filename):
    '''
    :param filename: file path
    :return: numpy.ndarray of the data split by '\t' and '\n'
        ps:the file should looks like a table,say it should have head and data
            which are seperated by '\t'
    '''
    f = file(filename,'r')
    ret = []
    for line in open(filename):
        line = f.readline().rstrip(u'\n')
        ret.append(line.split(u'\t'))
    ret = np.array(ret)
    return ret

def readtable(filename):
    '''
    :param filename: file path
    :return: pandas.DataFrame,it's a table
    '''
    data = readdata(filename)
    return pd.DataFrame(data[1:-1],columns=data[0])

def random_nodup(numlist):
    '''
    fetch a number in numlist randomly,then remove it from the list
    :param numlist: list of numbers,you can generate it from range(...) etc.
    :return: a number in the list
    '''
    index = randint(0,numlist.__len__()-1)
    num = numlist[index]
    numlist.remove(num)
    return num
