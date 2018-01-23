#coding=utf-8
from common import *
from fractions import Fraction
import numpy as np

def test():
    trainsetselection = 1
    if trainsetselection == 1:
        clf = NB(readtable('data/naivebayes_trainset.txt'))
        topred = readdata('data/naivebayes_topred.txt')
    else:
        clf = NB(readtable('data/decisiontree.txt'))
        topred = readdata('data/decisiontree_topred.txt')
    #print clf.classdict
    print clf.predict(topred)

class CNBValue():
    def __init__(self,value):
        '''
        a value e.g.:young,False,excellent,...
        :param value:
        '''
        self.value = value
        self.count = 0
        self.sup = Fraction(0,1)

    def calcSup(self, classsupcount, lambda_):
        '''
        :param classsupcount:
        :param lambda_: lambda
        :return:
        '''
        self.sup = Fraction(self.count + lambda_, classsupcount + lambda_)
        return self.sup

class CNBAttribute(dict):
    def __init__(self,attrname):
        '''
        An NBAttribute has many values,self is a dict{value:NBValue} in essence
        :param attrname:
        '''
        dict.__init__(self)
        self.name = attrname

    def checkValue(self,value):
        '''
        if self has this value
        then self[value].count+=1,self[value] is an object of NBValue
        else add self[value]=CNBValue(value),who's count=1
        :param value:
        :return:NBValue who's value == value
        '''
        if(dict.has_key(self,value)):
            nbv = dict.__getitem__(self,value)
            nbv.count += 1
        else:
            nbv = CNBValue(value)
            nbv.count = 1
            dict.__setitem__(self,value,nbv)
        return nbv

    def calcSup(self, classsupcount, lambda_):
        '''
        :param classsupcount: class.count counted in dataset
        :param lambda_:
        :return:
        '''
        self.classsupcount = classsupcount
        self.lambda_ = lambda_
        for nbv in self.values():
            nbv.calcSup(classsupcount, lambda_)

    def __getitem__(self, item):
        '''
        create value if not exists
        :param item: value
        :return:NBValue object who's value == item
        '''
        if(dict.has_key(self,item)):
            nbv = dict.__getitem__(self,item)
        else:
            nbv = CNBValue(item)
            nbv.calcSup(self.classsupcount,self.lambda_)
            dict.__setitem__(self,item,nbv)
        return nbv

class CNBClass(list):
    def __init__(self, classname, attributenamelist):
        '''
        a NBClass has several NBAttributes
        :param classname:
        :param attributenamelist:NBAttributes' name
        '''
        list.__init__(self)
        self.label = classname
        self.classid = attributenamelist[-1]
        self.count = 0
        self.sup = Fraction(0,1)
        for name in attributenamelist[0:attributenamelist.__len__()-1]:
            self.append(CNBAttribute(name))

    def calcSup(self, examplecount, lambda_):
        '''
        calculate self's sup and sup of all values
        :param examplecount: quantity of examples in dataset
        :param lambda_:
        :return: self.sup
        '''
        self.sup = Fraction(self.count, examplecount)
        for nba in self:
            nba.calcSup(self.count, lambda_)
        return self.sup

    def __str__(self):
        s = '------class {}------\n'.format(self.label)
        s += '-Pr({}={})={}\n'.format(self.classid,self.label,self.sup)
        for nba in self:
            for nbv in nba.values():
                s += '--Pr({}={}|{}={})={}\n'.format(nba.name,nbv.value,self.classid,self.label,nbv.sup)
        s += '--END-class {}-END--'.format(self.label)
        return s


class CNBClassDict(dict):
    def __init__(self, attributenamelist):
        '''
        NBClassDict is a dict{classname:NBClass}
        :param attributenamelist:
        '''
        dict.__init__(self)
        self.rulecount = 0
        self.attributenamelist = attributenamelist

    def checkClass(self,classname):
        '''
        create if not exists
        :param classname:
        :return: a CNBClass whos name's classname
        '''
        if(dict.has_key(self,classname)):
            nbc = dict.__getitem__(self,classname)
            nbc.count += 1
        else:
            nbc = CNBClass(classname,self.attributenamelist)
            nbc.count = 1
            dict.__setitem__(self,classname,nbc)
        self.rulecount += 1
        return nbc

    def calcSup(self):
        '''
        calculate sup of all classes in self
        :return:
        '''
        lambda_ = Fraction(1 , self.rulecount)
        for nbc in self.values():
            nbc.calcSup(self.rulecount,lambda_)

    def __str__(self):
        s = '::::::NBRuleDict::::::\n'
        for nbc in self.values():
            s += nbc.__str__() +'\n'
        s += '::END:NBRuleDict:END::'
        return s

class CNBRule(list):
    def __init__(self,defaultlabel=''):
        '''
        can be used to check whether prediction is right or wrong
        :param defaultlabel:
        '''
        self.classlabel = ''
        self.sup = Fraction(0,1)
        self.labellist = []  #the member not declared in init will be treated as static member
        self.defaultlabel = defaultlabel
        list.__init__(self)

    def __str__(self):
        s = ''
        if(self.classlabel == self.defaultlabel):
            s += 'V(Right)--\t'
        else:
            s += 'X(Wrong)--\t'
        for value in self:
            s += value.__str__() + '\t\t'
        s += 'Class={} Pr={}'.format(self.classlabel,self.sup)
        #s +=' ---other '
        #for t in self.labellist:
        #    s += 'P({})={}\t'.format(t[0],t[1])
        return s

    def checkLabel(self, label, probability):
        '''
        when sup is greater than the sup of self's classlabel
        then set current classlabel to (param label),and update self's sup
        :param label:a string represents self's class
        :param probability:label's probability calculated by NaiveBayes method
        :return:None
        '''
        newlabel = (label, probability)
        self.labellist.append(newlabel)
        if(probability > self.sup):
            self.sup = probability
            self.classlabel = label

class CNBRuleList(list):
    def __str__(self):
        s = ''
        for nbr in self:
            s += nbr.__str__() + '\n'
        return s

class NB():
    def __init__(self,trainingset):
        '''
        classifier with NaiveBayes algorithm
        :param trainingset:table(pandas.DataFrame)
        '''
        attributenamelist = list(trainingset.columns)
        self.classdict = CNBClassDict(attributenamelist)
        for rule in trainingset.itertuples():
            classlabel = rule[-1]
            nbc = self.classdict.checkClass(classlabel)
            i = 0
            for value in rule[1:rule.__len__()-1]:
                nbc[i].checkValue(value)
                i += 1
        self.classdict.calcSup()

    def predict(self,data):
        '''
        predict data's most probable classlabel
        :param data: 1 data or a list of data
        :return:a rule with classlabel or a list of such rules
        '''
        if(isinstance(data[0],np.ndarray)):
            result = CNBRuleList()
            for rule in data:
                result.append(self.predict(rule))
            return result
        else:
            defaultlabel = data[-1]
            result = CNBRule(defaultlabel)
            result.extend(data[0:data.__len__()-1])
            for nbc in self.classdict.values():
                sup = nbc.sup
                i = 0
                for value in data[0]:
                    sup *= nbc[i][value].sup
                    i += 1
                result.checkLabel(nbc.label,sup)
            return result

