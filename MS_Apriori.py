#coding=utf-8
from common import *
from fractions import Fraction
from Apriori import CItem,CTransaction,CTransList,CRule,CFrequentSetList

def test():
    data = readdata('data/ms_apriori.txt')
    #first two lines of data are Item's name and Item's MIS
    MISFloat = [float(x) for x in data[1]]
    MS = dict(zip(data[0],MISFloat))
    #the rest of data are Trasactions
    testDS = data[2:]
    result=MS_Apriori(testDS,MS,1,0.0)
    print result.genRules()

class CMISItem(CItem):
    def __init__(self,name,MIS=0,supCount=0,sup=Fraction(0,1)):
        '''
        Item with minimum support
        :param name:
        :param MIS:
        :param supCount:
        :param sup:
        '''
        CItem.__init__(self,name,supCount,sup)
        self.MIS = MIS

class CMSATrans(CTransaction):
    def __init__(self,item = CMISItem('')):
        '''
        Transaction of MISItems
        :param item:
        '''
        CTransaction.__init__(self,item)

    def sort(self, cmp = None, key=None, reverse=False):
        '''
        sort by MIS,if several items have same MIS then sort them by name
        :param cmp:
        :param key:
        :param reverse:
        :return:
        '''
        if(key == None):
            key = key=lambda x:str(x.MIS)+x.name
        list.sort(self,key=key,reverse=reverse)

class CMSARule(CRule):
    def __init__(self,transaction,pioneer,conf=0.0):
        '''
        it's similiar with CRule
        :param transaction:
        :param pioneer:
        :param conf:
        '''
        CRule.__init__(self,transaction,pioneer,conf)


class MS_Apriori():
    def __init__(self,T,MS,fai,minConf):
        '''
        MS Pariori P23 ,2018.01.23
        :param T:Transactions numpy.ndarray
        :param MS:Minimum support of each kind of item
        :param fai:M={MIS(item1),MIS(item2),...}
                    φ>max(M) - min(M)
        :param minConf:min confidence of MISRule which is reserved
        '''
        self.fai = fai
        self.minConf = minConf
        self.F = CFrequentSetList('MS_Apriori.F')
        self.Rules = CTransList('MS_Apriori.Rules')
        self.T = CTransList('T')
        #convert MIS dict into MIS CItem dict
        dupMS = MS.copy()
        for key in dupMS.keys():
            dupMS[key] = CMISItem(key, dupMS[key])
        #data conversion
        #count supCount
        for t in T:
            transaction = CMSATrans()
            for i in t:
                transaction.append(dupMS[i])
                dupMS[i].supCount += 1
            transaction.sort()
            self.T.append(transaction)
        #calculate sup for items
        for item in dupMS.values():item.calcSup(T)

        #MS-Apriori
        #M is a list of MISItem sorted by MIS
        M = [x[1] for x in sorted(dupMS.items(),key=lambda x:x[1].MIS)]#[CItem]
        L=CTransList('L') #1-item transaction
        #L is a 1-item Transactions list where:
            #l is the first item who satisfies l.sup>=l.MIS
            #L contains the items in M who satisfy item.sup>=l.MIS
        for i in range(M.__len__()):#L←init-pass(M,T)
            l = M[i]
            if(l.sup >= l.MIS):
                MISl = l.MIS
                for i in range(i,M.__len__()):
                    l = M[i]
                    if(l.sup >= MISl):
                        L.append(CMSATrans(l))
                break
        F1 = CTransList('F1') #F1←{{l}|l∈L,l.count/n>=MIS(l)}
        for l in L:
            if(l.sup >= l[0].MIS):
                F1.append(l)

        k = 2
        Fk_1 = F1
        while(Fk_1.__len__()>0):
            Fk = CTransList('F'+str(k))
            if(k == 2):
                Ck = self._level2_candidate_gen(L, fai)
            else:
                Ck = self._MScandidate_gen(Fk_1, fai)
            for t in self.T:
                for c in Ck:
                    if(c in t):
                        c.supCount += 1
                    if(c[1:c.__len__()] in t):
                        if(hasattr(c,'cec1sc')):
                            setattr(c, 'cec1sc', getattr(c, 'cec1sc') + 1)  # (c without c[0])'s supCount
                        else:
                            setattr(c,'cec1sc',1)
            for c in Ck:
                c.calcSup(T)
                if(c.sup >= c[0].MIS):
                    Fk.append(c)
            self.F.append(Fk_1)
            Fk_1 = Fk
            k += 1
        #printList(self.F,'F Collections:')

    def _level2_candidate_gen(self, L, fai):
        '''
        generate C2 with L
        :param L:
        :param fai:
        :return:C2
        '''
        C2 = CTransList('C2')
        for i in range(L.__len__()-1):
            l = L[i]
            if(l.sup > l[0].MIS):
                for j in range(i+1,L.__len__()):
                    h = L[j]
                    if(h.sup >= l[0].MIS and abs(h.sup - l.sup)<=fai):
                        C2.append(l+h)
        return C2

    def _MScandidate_gen(self, Fk_1, fai):
        '''
        generate Fk with Fk-1
        :param Fk_1:
        :param k:
        :param fai:
        :return:Ck
        '''
        k = Fk_1.k + 1
        Ck = CTransList('C'+str(k))
        for i in range(Fk_1.__len__()):
            f1 = Fk_1[i]
            for j in range(i+1,Fk_1.__len__()):
                f2 = Fk_1[j]
                if(f1[0:k-2] == f2[0:k-2] and abs(f2[k-2].sup - f1[0].sup)<=fai):#ik-1<i'k-1  ?这是什么意思
                    c = f1 + f2[k - 2:k-1]
                    Ck.append(c)
                    for x in range(k):
                        s = c[0:x] + c[x + 1:c.__len__()]
                        if(c[0] in s
                           or (c[0].MIS==c[1].MIS)):
                            if(s not in Fk_1):
                                Ck.remove(c)
                                break
        return Ck

    def genRules(self):
        '''
        generate rules
        :return: self.Rules
        '''
        k = 2
        for k in range(k, self.F.__len__()):
            for fk in self.F[k]:
                H1 = CTransList('H1')
                for i in range(0,fk.__len__()):
                    item = fk[i]
                    if(i == 0):
                        X = fk - CMSATrans(item)
                        if(hasattr(fk,'cec1sc')):
                            X.supCount = getattr(fk,'cec1sc')
                    else:
                        X = self.F[k-1].matchTransaction(fk - CMSATrans(item))  #match to get supCount X->Y
                    conf = Fraction(fk.supCount , X.supCount)
                    if (conf >= self.minConf):
                        self.Rules.append(CMSARule(fk, X, conf))
                        H1.append(CMSATrans(item))
                self._ap_genRules(fk, H1)
        return self.Rules

    def _ap_genRules(self, fk, Hm):
        '''
        :param fk:a frequent transaction in Fk
        :param Hm: consequents of all m-item consequent rules derived from fk
        :param m:
        :return:None
        '''
        m = Hm.k
        k = fk.__len__()
        if (k > m + 1 and Hm.__len__() > 0):
            Hm1 = MS_Apriori.candidate_gen(Hm)  # Hm1 means Hm+1
            for hm1 in Hm1:
                fk_hm1 = fk - hm1
                fk_hm1 = self.F[k-m-1].matchTransaction(fk_hm1)
                conf = Fraction(fk.supCount , fk_hm1.supCount)
                if conf >= self.minConf:
                    self.Rules.append(CMSARule(fk, fk_hm1, conf))
                else:
                    Hm1.remove(hm1)
            self._ap_genRules(fk, Hm1)

    @staticmethod
    def candidate_gen(Fk_1):
        '''
        generate Ck from Fk_1
        :param Fk_1:
        :return:Ck
        '''
        i, j = 0, 0
        Ck =CTransList('None')
        k = 0
        if (Fk_1.__len__() > 0):
            k = Fk_1[0].__len__() + 1
            Ck = CTransList('C'+k.__str__())
            for i in range(Fk_1.__len__()):
                for j in range(i + 1, Fk_1.__len__()):
                    tki = Fk_1[i]
                    tkj = Fk_1[j]
                    if (tki[0:k-2] == tkj[0:k-2]):
                        candidate = tki + tkj[k-2: k-1]
                        if (candidate[1:k] in Fk_1):
                            Ck.append(candidate)
            return Ck
        else:
            return Ck

