#coding=utf-8
import uniout

from common import *
from fractions import Fraction

def test():
    dataSet = [
        ['牛肉', '鸡肉', '牛奶'],
        ['牛肉', '奶酪'],
        ['奶酪', '靴子'],
        ['牛肉', '鸡肉', '奶酪'],
        ['牛肉', '鸡肉', '衣服', '奶酪', '牛奶'],
        ['鸡肉', '衣服', '牛奶'],
        ['鸡肉', '牛奶', '衣服']
    ]

    result = Apriori(dataSet,0.3,0.8)
    print result.F
    printList(result.F,'Apriori.F')
    Rules = result.genRules()  # dataSet,minsup,minconf
    print Rules

class CItem(object):
    name= ''
    sup=Fraction(0,1)
    supCount=0
    def __init__(self,name,supCount=0,sup=Fraction(0,1)):
        self.name = name
        self.sup = sup
        self.supCount = supCount

    def key(self):
        return self.name

    def calcSup(self,T):#calculate item.count/n
        self.sup = Fraction(self.supCount , T.__len__())

    def namestr(self):
        return self.name.__str__()

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.name.__str__()

class CTransaction(list): #事务的项目按照MIS排序，如果MIS相同则按照事务名称的字典序排列
    supCount,sup = 0,Fraction(0,1)
    def __init__(self, item=CItem('')):
        list.__init__([])
        if(type(item) == CTransaction):
            self.sup = item.sup
            self.supCount = item.supCount
            self.extend(item)
        else:
            if (item.name != ''):
                self.sup = item.sup
                self.supCount = item.supCount
                self.append(item)

    def getSupCount(self,transanctionList):
        self.supCount = 0
        for t in transanctionList:
            if(self in t):
                self.supCount += 1
        self.sup = self.calcSup(transanctionList)
        return self.supCount

    def checkSupportDifferenceConstraint(self,fai):#支持度差别限制,return true if fit
        ret = self[self.__len__()-1].sup - self[0] <= fai

        return ret

    def calcSup(self,T):
        self.sup = Fraction(self.supCount,T.__len__())
        return self.sup

    def sort(self, cmp = None, key=None, reverse=False):#sort by MIS,if several items have same MIS then sort them by name
        list.sort(self,key=lambda x:x.name,reverse=reverse)

    def __getslice__(self, start, stop): #sub transaction
        t = CTransaction()
        t.extend(list.__getslice__(self, start,stop))
        return t

    def __contains__(self, item):
        if(isinstance(item,list)):
            i = 0
            for itm in self:
                if(itm == item[i]):
                    i += 1
                    if(i == item.__len__()):
                        return True
        else:
            return list.__contains__(self,item)
        return False

    def __sub__(self, other):
        t = CTransaction()
        i = 0
        for item in self:
            if(i < other.__len__()):
                if (item != other[i]):
                    t.append(item)
                else:
                    i += 1
            else:
                t.append(item)
        return t

    def __add__(self, other):  # 没有检查重复项，返回新的结合事件,AUB
        t = self[:]
        t.extend(other)
        t.sort()
        return t

    def __str__(self):
        s = '{'
        for i in range(self.__len__()):
            s += self[i].__str__()
            if(i < self.__len__()-1):
                s += ','
        s +='}'
        s1 = '<sup={}>'
        s += s1.format(self.sup)
        return s

    def __eq__(self, other):#if the name of each items in self and other is same,return True
        i = 0
        if(self.__len__() != other.__len__()):
            return False
        for item in self:
            if(item == other[i]):
                i += 1
            else:
                return False
        return True

    def __supcount__(self):return self.supCount
    def __sup__(self):return self.sup

class CTransList(list):
    name = ''
    def __init__(self,name):
        list.__init__([CItem])
        self.name = name

    def matchTransaction(self,transactionB):#match a same transaction and return it,to get sup etc.
        for t in self:
            if(t == transactionB):
                return t
        return None

    def __contains__(self, item):
        for t in self:
            if(t == item): #compare transaction
                return True
        return False

    def __str__(self):
        s = '_______________________\n'
        s += self.name + ':\n'
        for t in self:
            s += '--' + t.__str__() + '\n'
        s+= '~~~~~~~~~~~~~~~~~~~~~~~'
        return s

class CFrequentSetList(list):
    def __init__(self,name,setlist=()):
        list.__init__(self,setlist)
        self.name = name

    def __str__(self):
        s = self.name + ':::::::START\n'
        for item in self:
            s += item.__str__() + '\n'
        s += self.name + '::::::::END'
        return s

class CRule(CTransaction):
    def __init__(self,transaction,pioneer,conf = 0.0):
        CTransaction.__init__(self,transaction)
        self.pioneer = pioneer
        self.conf = conf

    def calcConf(self):
        self.conf = Fraction(self.supCount,self.pioneer.supCount)
        return self.conf

    def calcSup(self,T):
        self.sup = Fraction(self.supCount,T.__len__())
        return self.sup

    def __str__(self):
        s = ''
        i = 0
        for item in self.pioneer:
            s += item.name
            i += 1
            if (i != self.pioneer.__len__()):
                s += ','
        s += '→'
        i = 0
        Y = self - self.pioneer
        for item in Y:
            s += item.name
            i += 1
            if (i != Y.__len__()):
                s += ','
        s += ' [sup={},conf={}]'.format(Fraction(self.sup).__str__(), self.conf)
        return s

class Apriori:
    def __init__(self,T, minsup,minconf):
        self.F = CFrequentSetList('Apriori.F',[CTransList('F0')])
        self.T = CTransList('T')
        self.Rules = CTransList('Apriori.Rules')
        self.minsup = minsup
        self.minconf = minconf
        C1 = self.init_pass(T)  # support count dict
        F1 = CTransList('F1')
        for c in C1:
            if c.calcSup(self.T) > minsup:
                F1.append(c)
        Fk_1 = F1
        k = 2
        while Fk_1.__len__() > 0:
            Fk = CTransList('F'+k.__str__())
            self.F.append(Fk_1)
            Ck = self.candidate_gen(Fk_1)
            for t in self.T:
                for c in Ck:
                    if c in t:
                        c.supCount += 1
            for c in Ck:
                if(c.calcSup(self.T) > minsup):
                    Fk.append(c)
            Fk_1 = Fk
            k += 1

    def init_pass(self,T):
        C1 = CTransList('C1')
        count = {}
        itemDict = {}
        for trans in T:
            transaction = CTransaction()
            for itm in trans:
                if(itemDict.has_key(itm)):
                    ci = itemDict[itm]
                    ci.supCount += 1
                else:
                    ci = CItem(itm,1)
                    itemDict[itm] = ci

                transaction.append(ci)
            transaction.sort()
            self.T.append(transaction)
        for ci in itemDict.values():
            C1.append(CTransaction(ci))
        return C1

    @staticmethod
    def candidate_gen(Fk_1):
        k = 0
        if (Fk_1.__len__() > 0):
            k = Fk_1[0].__len__() + 1
        else:
            return CTransList('Null TransList')
        Ck = CTransList('C'+k.__str__())
        for i in range(Fk_1.__len__()):
            tki = Fk_1[i]
            for j in range(i + 1, Fk_1.__len__()):
                tkj = Fk_1[j]
                if (tki[0:k-2] == tkj[0:k-2]):
                    candidate = tki[:]
                    candidate.append(tkj[k-2])
                    if (candidate[1:k] in Fk_1):
                        Ck.append(candidate)
        return Ck

    def genRules(self):
        for k in range(2,self.F.__len__()):
            for fk in self.F[k]:
                H1 = CTransList('H1')
                for i in range(0, fk.__len__()):
                    consequent = CTransaction(fk[i])
                    H1.append(consequent)
                    pioneer = fk - consequent
                    pioneer = self.F[fk.__len__() - 1].matchTransaction(pioneer)
                    r = CRule(fk, pioneer)
                    if (r.calcConf() >= self.minconf):
                        self.Rules.append(r)
                self.ap_genRules(fk, k, H1, 1)
        return self.Rules

    def ap_genRules(self,fk, k, Hm, m):
        if (k > m + 1 and Hm.__len__() > 0):
            Hm1 = Apriori.candidate_gen(Hm)  # Hm1 means Hm+1
            for hm1 in Hm1:
                fk_hm1 = fk - hm1
                fk_hm1 = self.F[k-m-1].matchTransaction(fk_hm1)
                r = CRule(fk,fk_hm1)
                if r.calcConf() >= self.minconf:
                    self.Rules.append(r)
                else:
                    #Hm1.remove(hm1)  #加这句会出错，导致循环次数减少，原因不明
                    pass
            self.ap_genRules(fk,k,Hm1,m+1)
