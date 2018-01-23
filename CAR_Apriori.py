#coding=utf-8
from common import *
from MS_Apriori import CTransaction,CTransList,CMSARule,Fraction,MS_Apriori,CFrequentSetList
from Apriori import CItem

def test():
    data = readdata('data/car_apriori.txt')
    result = CAR_Apriori(data,0.2,0.6)
    print result.CAR

class CCARule(CTransaction):
    def __init__(self,item=CItem(''),class_='',rulesupCount=0):
        '''
        if item is provided,init self with item's data
        :param item:CItem object
        :param class_:self's class label
        :param rulesupCount:supcount of this rule
        '''
        CTransaction.__init__(self,item)
        self.rulesupCount = rulesupCount
        self.class_ = class_

    def calcConf(self):
        self.conf = Fraction(self.rulesupCount,self.supCount)
        return self.conf

    def calcSup(self,T):
        self.sup = Fraction(self.rulesupCount,T.__len__())
        return self.sup

    def __getslice__(self, start, stop):
        '''
        :param start:
        :param stop:
        :return: CCARule object
        '''
        r = CCARule()
        r.extend(CTransaction.__getslice__(self,start,stop))
        return r

    def __add__(self, other):
        '''
        return a new CCARule n,n=self+other
        :param other:another Rule
        :return:
        '''
        r = CCARule()
        r.extend(self)
        r.extend(other)
        r.sort()
        return r

    def __str__(self):
        s = ''
        i = 1
        for item in self:
            s += item.name
            if(i < self.__len__()):
                i+=1
                s +=','
        s += '→'
        s += self.class_ + '[sup={},conf={}]'.format(self.sup,self.conf)
        return s

class CCARList(CTransList):
    def __init__(self,name):
        CTransList.__init__(self,name)

class CAR_Apriori():
    def __init__(self,T,minsup,minconf):
        '''
        CAR_Apriori P29,2018.12.23
        :param T:dataset(numpy.ndarray),see car_apriori.txt
        :param minsup:minimum support
        :param minconf:minimum confidence
        '''
        self.T = CCARList('T')
        self.CAR = CFrequentSetList('CAR_Apriori.CAR', CCARList('CCAR0'))  # [CCARList]
        #covert dataSet,convert T to self.T
        C1 = self.init_pass(T)
        F1 = CCARList('F1')
        CAR1 = CCARList('CAR1')
        for f in C1:
            if(f.calcSup(self.T) >= minsup):
                F1.append(f)
                if (f.calcConf() >= minconf):
                    CAR1.append(f)
        self.CAR.append(CAR1)
        k = 2
        Fk_1 = F1
        while(Fk_1.__len__()>0):
            Ck = self.CARcandidate_gen(Fk_1)
            Fk = CCARList('F' + str(k))
            CARk = CCARList('CAR'+str(k))
            for t in self.T:
                for c in Ck:
                    if(c in t):
                        c.supCount += 1
                        if(t.class_ == c.class_):
                            c.rulesupCount += 1
            for c in Ck:
                if(c.calcSup(self.T) >= minsup):
                    Fk.append(c)
            for f in Fk:
                if(f.calcConf() >= minconf):
                    CARk.append(f)
            if(CARk.__len__() > 0):
                self.CAR.append(CARk)
            Fk_1 = Fk
            k += 1

    def CARcandidate_gen(self,Fk_1):
        if (Fk_1.__len__() == 0): return CCARList('None')
        Ck = CCARList('C' + str(Fk_1[0].__len__() + 1))
        class_ = 'null'
        newFk_1 = CCARList('newFk_1')
        sentinel = CCARule(class_ = class_)
        Fk_1.append(sentinel) #guard
        for r in Fk_1:
            if(class_ == r.class_):
                newFk_1.append(r)
            else:
                if(class_ != 'null'):
                    for item in MS_Apriori.candidate_gen(newFk_1):
                        item.class_ = class_
                        item.sort()
                        Ck.append(item)
                class_ = r.class_
                newFk_1 = CCARList('newFk_1')
                newFk_1.append(r)
        Fk_1.remove(sentinel)#remove guard
        return Ck

    def init_pass(self,T):
        C1 = CCARList('C1')
        ruleDict={} #name-class:item
        itemDict={}#name:item
        car = CCARule()
        ci = CItem('')
        for rule in T:
            trule = CCARule()
            trule.class_ = rule[-1]
            for item in rule[0:-1]:
                name_class = item + trule.class_
                if (itemDict.has_key(item)):
                    ci = itemDict[item]
                    ci.supCount += 1
                else:
                    ci = CItem(item,1)
                    itemDict[item] = ci
                trule.append(ci)
                #gen 1-  rule
                if(ruleDict.has_key(name_class)):
                    car = ruleDict[name_class]
                    car.rulesupCount += 1
                    car.supCount = ci.supCount #condsupCount
                else:
                    car = CCARule(ci,trule.class_,1)
                    ruleDict[name_class] = car
                    C1.append(car)
            trule.sort()
            self.T.append(trule)
        return  C1

