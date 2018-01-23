#-*-coding=utf-8
from common import *
import TreePlot
import pandas as pd
import math
import numpy as np
import random as rd
from fractions import Fraction

def test():
    data = readdata('data/decisiontree.txt')
    clf = decisionTree(data[1:],data[0],gainthreshold=0.02,trainset=0.8)
    testdata = readdata('data/decisiontree_topred.txt')
    for data in testdata:
        print clf.predict(data)
    clf.show('loan_application')
    pass

class TreeNode(TreePlot.TreePlotNode):
    def __init__(self,name):
        '''
        :param name:tree-node's infomation
        '''
        TreePlot.TreePlotNode.__init__(self)
        self.name = name
        self.type = 'node'
        self.shape = 'rectangle'
        self.color = ('blue','yellow','green','purple')[rd.randint(0,3)]

    def content(self):
        return self.name

    def search(self,data):#data should be dict like
        '''
        search data in tree recursively,and mark the path of this data in tree graph
        with red(color)
        :param data:1 data
        :return:
        '''
        self.color = 'red'
        if(self.type == 'leaf'):
            return self.name
        value = data[self.name]
        edge = self.edges[value]
        edge.color = 'red'
        nextnode = edge.endnode
        return nextnode.search(data)

class TreeLeaf(TreeNode):
    def __init__(self, name, probability):
        '''
        Leaf is derived from Node,so it is a Node in essence
        but it will be drawed in different shape with node in the graph
        :param name:leaf info
        :param probability:this leaf's sup
        '''
        TreeNode.__init__(self,name)
        self.name = name
        self.type = 'leaf'
        self.shape = 'ellipse'
        self.percentage = probability

    def content(self):
        return self.name + '\n' + self.percentage.__str__()

class TreeEdge(TreePlot.TreePlotEdge):
    def __init__(self,name,startnode=None,endnode=None):
        '''
        Edge
        :param startnode:
        :param endnode:
        :param name: string shown on edge
        '''
        TreePlot.TreePlotEdge.__init__(self,startnode,endnode)
        self.color = ( 'blue', 'yellow', 'green', 'purple')[rd.randint(0, 3)]
        self.name = name

    def content(self):
        return self.name

class decisionTree:
    '''
    D :dataset(numpy.array),include label column
    A :attributes(numpy.array),table head
    gainthreshod :when gain of entropy reduction is less than it,stop expand tree
    trainset :get testset from D,test's size = D.size*(D.size-trainset)
    what's more:
        you can expand testset by using decisionTree.test.append() or .extend()
    '''
    def __init__(self,D,A,gainthreshold=0.001,trainset=1.0):
        self.A = A[0:A.__len__()-1]
        self.labelcolumn = A[-1]
        testset = []
        if(trainset == 1.0):
            trainset = D
        else:
            # split D into trainset and test set
            total = D.shape[0]
            randnumlist = range(total)
            trainsetlen = int(total * trainset)
            testsetlen = total - trainsetlen
            trainset = []
            for i in range(trainsetlen):
                trainset.append(D[random_nodup(randnumlist)])
            for i in range(testsetlen):
                testset.append(D[random_nodup(randnumlist)])
        self.D = pd.DataFrame(trainset, columns=A)
        self.testset = testset
        self.infonode = None
        self.tree = None
        self.threshold = gainthreshold
        self._createtree(self.D,self.A,self.tree)
        self._evaluate()
        pass

    def show(self,name):
        '''
        display tree in graph mode
        :param name: title of graph,or say name of the .pdf file
        :return:None
        '''
        showtree = self.tree
        if(self.infonode != None):
            showtree = self.infonode
        plt = TreePlot.TreePlot(showtree,name)
        plt.show()

    def predict(self,data):
        '''
        predict an unknown data's label
        :param data:1D(numpy.array)
        :return:classlabel of data
        '''
        data = dict(zip(self.A,data))
        return self.tree.search(data)

    ####### private members #########
    def _evaluate(self):
        if(self.testset.__len__() == 0):
            return
        rightcount = 0.0
        for row in self.testset:
            pred = self.predict(row)
            actual = row[-1]
            if(pred == actual):
                rightcount += 1
        s = u'Testset size:{}\n'.format(self.testset.__len__())
        s += u'Correct rate:{}%'.format(rightcount*100/self.testset.__len__())
        self.infonode = TreeNode(s)
        self.infonode.appendchild(self.tree)
        print s

    def _createtree(self,D,A,parentnode,edgename=''):
        label = D[[self.labelcolumn]].drop_duplicates()
        if (label.__len__() == 1):  # if D contains only training examples of the same class cj∈C then
            label = label.at[0,self.labelcolumn]
            leaf = TreeLeaf(label,Fraction(1,1))
            if(parentnode == None):
                self.tree = leaf  # make T a leaf node labeled with class cj
            else:
                parentnode.appendchild(leaf,TreeEdge(edgename))
        elif A.__len__() == 0:  # else if A=∅ then
            # make T a leaf node labeled with cj,which is the most frequent class in D
            mostfreqclass, percent = self._mostfrequentclass(D)
            leaf = TreeLeaf(mostfreqclass, percent)
            if(parentnode == None):
                self.tree = leaf
            else:
                parentnode.appendchild(leaf,TreeEdge(edgename))
        else:  # D contains examples belonging to  a mixture of classes.We select a single
            # attribute to partition D into subsets so that each subset is purer
            p0 = self._impurityEval_1(D)
            pg,Ag = 1,None
            for Ai in A:
                pi = self._impurityEval_2(Ai, D)
                if(pi < pg):
                    pg = pi
                    Ag = Ai
            if(p0 - pg < self.threshold):
                #make T a leaf node labeled with cj,the most frequent class in D.
                mostfreqclass,percent = self._mostfrequentclass(D)
                leaf = TreeLeaf(mostfreqclass,percent)
                if(parentnode == None):
                    self.tree = leaf
                    parentnode = self.tree
                else:
                    parentnode.appendchild(leaf,TreeEdge(edgename))
            else:
                leaf = TreeNode(Ag)
                if(parentnode == None):
                    self.tree = leaf
                else:
                    # make T a decision node on Ag
                    parentnode.appendchild(leaf, TreeEdge(edgename))
                Dl, Vl = self._partition(Ag, D)
                j = 0
                for Dj in Dl:
                    Vj = Vl[j]
                    if (Dj.__len__() > 0):
                        A_Ag = list(A[:])
                        A_Ag.remove(Ag)
                        A_Ag = np.array(A_Ag)
                        self._createtree(Dj, A_Ag, leaf, Vj)
                    j += 1

    def _mostfrequentclass(self,D):
        label = D[[self.labelcolumn]]
        label.insert(0, 'count', 0)
        label = label.groupby(self.labelcolumn).count()
        label = label.reset_index()
        label = label.max()
        percent = Fraction(label['count'] , D.__len__())
        mostfreqclass = label[self.labelcolumn]
        return mostfreqclass,percent

    def _impurityEval_1(self,D):
        C = D[[self.labelcolumn]]
        C.insert(0,'count',0)
        C = C.groupby(self.labelcolumn).count()
        total = D.__len__()
        entropyD = 0.0
        for row in C.itertuples(index=False):
            Prcj = float(row[0]) / total
            entropyD += -(Prcj * math.log(Prcj,2))
        return entropyD

    def _impurityEval_2(self,Ai,D):
        entropyAiD = 0.0
        #divide D with Ai
        Dl,Vl = self._partition(Ai,D)
        total = D.__len__()
        for Dj in Dl:
            Djtotal = Dj.__len__()
            entropyDj = self._impurityEval_1(Dj)
            entropyAiD += (Djtotal * entropyDj / total)
        return entropyAiD

    def _partition(self,Ag,D):#return list of patitioned D,and values who response partitioning
        Dl = []
        Dx = D.groupby(Ag).count().reset_index()
        Vl = []
        for value in Dx[[Ag]].itertuples(index=False):
            value = value[0]
            Dj = D[D[Ag] == value].reset_index(drop=True)
            Dl.append(Dj)
            Vl.append(value)
        return Dl,Vl

