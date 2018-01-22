#coding=utf-8
from common import *
from MS_Apriori import CTransaction,CTransList,CMSARule,Fraction,MS_Apriori,CFrequentSetList
from Apriori import CItem

def test():
    docSet = [
        (['学生','授课','学校'],       '教育'),
        (['学生','学校'],              '教育'),
        (['授课','学校','城市','游戏'], '教育'),
        (['棒球','篮球'],              '体育'),
        (['篮球','球员','观众'],       '体育'),
        (['棒球','教练','游戏','球队'], '体育'),
        (['篮球','球队','城市','游戏'], '体育')
    ]
    result = CAR_Apriori(docSet,0.2,0.6)
    print result.CAR
    pass

class CCARule(CTransaction):
    conf = 0.0
    class_ = ''
    rulesupCount = 0
    def __init__(self,item=CItem(''),class_='',rulesupCount=0):
        CTransaction.__init__(self,item)
        self.rulesupCount = rulesupCount
        self.class_ = class_

    def calcConf(self):
        self.conf = Fraction(self.rulesupCount,self.supCount)
        return self.conf

    def calcSup(self,T):
        self.sup = Fraction(self.rulesupCount,T.__len__())
        return self.sup

    def sort(self, cmp = None, key=None, reverse=False):
        if(key == None):
            key = lambda x:x.name
        list.sort(self,key = key,reverse=reverse)

    def __getslice__(self, start, stop):
        r = CCARule()
        r.extend(CTransaction.__getslice__(self,start,stop))
        return r

    def __add__(self, other):#没排序
        r = CCARule()
        r.extend(self)
        r.extend(other)
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
        self.T = CCARList('T')
        self.CAR = CFrequentSetList('CAR_Apriori.CAR', [CCARList('CCAR0')])  # [CCARList]
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
            TRule = CCARule()
            TRule.class_ = rule[1]
            for item in rule[0]:
                name_class = item + rule[1]
                if (itemDict.has_key(item)):
                    ci = itemDict[item]
                    ci.supCount += 1
                else:
                    ci = CItem(item,1)
                    itemDict[item] = ci
                TRule.append(ci)
                #gen 1-  rule
                if(ruleDict.has_key(name_class)):
                    car = ruleDict[name_class]
                    car.rulesupCount += 1
                    car.supCount = ci.supCount #condsupCount
                else:
                    car = CCARule(ci,rule[1],1)
                    ruleDict[name_class] = car
                    C1.append(car)
            TRule.sort()
            self.T.append(TRule)
        return  C1

