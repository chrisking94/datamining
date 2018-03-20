#coding=utf-8
from common import *
from fractions import Fraction
import numpy as np

def test():
    trainsetselection = 1
    if trainsetselection == 1:
        clf = NB(readtable('data/naivebayes_trainset.txt'))
        clf.train()
        topred = readdata('data/naivebayes_topred.txt')
    else:
        clf = NB(readtable('data/decjsiontree.txt'))
        clf.train()
        topred = readdata('data/decjsiontree_topred.txt')
    #print clf.classdict
    print clf.predict(topred)

class NB():
    def __init__(self,trainset):
        '''
            classifier with NaiveBayes algorithm
            :param trainingset:table(pandas.DataFrame)
        '''
        self.trainset = trainset
        self.classdict = None
        self.nvecdim = -1

    def train(self,trainset=None):
        if(trainset is None):
            trainset = self.trainset
            if(trainset is None):
                raise Exception('error:there\'s no trainset!')
        wordindexer = {}#word index-er
        classdict = {}
        wordindex = 0
        i = 0
        for doc in trainset.itertuples(index=False):
            cla = doc[-1] #class label
            if(not classdict.has_key(cla)):#classify doc into the class its belongs to
                classdict[cla] = []
            doc=doc[:doc.__len__()-1]
            vector = [0] * (wordindex)
            for word in doc:
                if(not wordindexer.has_key(word)):
                    wordindexer[word] = wordindex
                    i = wordindex
                    wordindex += 1
                    vector.append(0)
                else:
                    i = wordindexer[word]
                vector[i] += 1
            classdict[cla].append(vector) #append doc vector to trainset
        self.wordindexer = wordindexer
        i = wordindex
        self.nvecdim = i
        for class_docs in classdict.iteritems():
            cla = class_docs[0]
            docs = class_docs[1]
            vec_wordscount = np.zeros(i)
            for doc in docs:
                # reshape vectors to the same dim
                doc.extend([0] * (i - doc.__len__()))
                vector = np.array(doc)
                vec_wordscount += vector
            vecP_w_cj = vec_wordscount / float(docs.__len__())
            P_cj = docs.__len__() / float(trainset.__len__())
            classdict[cla] = (vecP_w_cj,P_cj)
        self.classdict = classdict

    def _docToVec(self,doc):
        '''
        convert document to vector
        :param doc:word list
        :return:vector converted from doc
        '''
        vecRet = np.zeros(self.nvecdim)
        for word in doc[:doc.__len__()]:
            if(self.wordindexer.has_key(word)):
                vecRet[self.wordindexer[word]] += 1
            else:
                print 'warning:[%s] never appears in training set,ignored!' % (word)
        return vecRet

    def predict(self,data):
        '''
        predict data's most probable classlabel
        :param data: 1 data or a list of data
        :return:a rule with classlabel or a list of such rules
        '''
        if(self.classdict == None):
            raise Exception('Please train NB firstly!')
        if(isinstance(data[0],np.ndarray)):
            result = []
            for rule in data:
                result.append(self.predict(rule))
            return result
        else:
            maxProb = 0
            mostProbClass = None
            vecData = self._docToVec(data)
            for class_probtuple in self.classdict.iteritems():
                cla = class_probtuple[0]
                vecPwcj = class_probtuple[1][0]
                Pcj = class_probtuple[1][1]
                vecP = vecData * vecPwcj
                P_cj_d = Pcj
                for p in vecP:
                    if(p != 0):
                        P_cj_d *= p
                if(P_cj_d > maxProb):
                    maxProb = P_cj_d
                    mostProbClass = cla
            return mostProbClass,maxProb

    def _crossValidation(self,testset=0.2,times=10):
        train = range(self.trainset.__len__())
        test = []
        testsize = self.trainset.__len__() * testset
        np.random