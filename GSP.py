#coding=utf-8

from MS_Apriori import CTransaction,CItem,CTransList
from Apriori import CFrequentSetList

def test():
    SequenceDataBase = [
        [[30],[90]],
        [[10,20],[30],[10,40,60,70]],
        [[30,50,70,80]],
        [[30],[30,40,70,80],[90]],
        [[90]]
    ]
    result = GSP(SequenceDataBase,0.25)
    print result.F
    pass

class CGSPElement(CTransaction):
    name = 'GSP_Element'

    def sort(self, cmp = None, key=None, reverse=False):
        list.sort(self,key = lambda x:x.name)

    def __getslice__(self, start, stop):
        element = CGSPElement()
        for itm in self:
            element.append(itm)
        return element

    def __str__(self):
        s = '{'
        i = 0
        for item in self:
            s += item.namestr()
            i += 1
            if(i < self.__len__()):
                s+=','
        s += '}'
        return s

class CSequence(CTransaction):
    def __init__(self, GSPEle = CGSPElement()):
        if(GSPEle.__len__()>0):
            CTransaction.__init__(self,GSPEle)
        else:
            CTransaction.__init__(self)

    def removeAt(self, index):
        i = 0
        for ele in self:
            for itm in ele:
                if(i == index):
                    ele.remove(itm)
                    if(ele.__len__() == 0):
                        list.remove(self,ele)
                        return self
                i += 1
        return self

    def getItemSequence(self, start, stop): #counted by items
        i = 0
        sequence = CSequence()
        element = CGSPElement()
        if(start >= stop):
            return sequence

        for ele in self:
            for itm in ele:
                if(i >= start):
                    element.append(itm)
                i += 1
                if(i == stop):
                    break
            if(i > start):
                sequence.append(element)
                if(i == stop):
                    return sequence
        return sequence

    def getitem(self, item):
        i = 0
        for ele in self:
            for itm in ele:
                if(i == item):
                    return itm
                else:
                    i += 1
        return None

    def itemCount(self):
        length = 0
        for ele in self:
            length += ele.__len__()
        return length

    def __getslice__(self, start, stop):
        s = CSequence()
        for ele in self:
            s.append(ele[:])
        return s

    def __contains__(self, item):
        if(isinstance(self,list)):
            #item is a sequence
            i = 0
            for ele in self:
                if (item[i] in ele):
                    i += 1
                    if(i == item.__len__()):
                        return True
            return False
        else:
            return CTransaction.__contains__(self,item)

    def __str__(self):
        s = '<'
        i = 0
        for trans in self:
            s += trans.__str__()
            i += 1
            if(i<self.__len__()):
                s += ','
        s += '> [sup={}]'.format(self.sup)
        return s

class CSeqList(CTransList):
    def __init__(self,name):
        CTransList.__init__(self,name)

class GSP:
    def __init__(self,S,minsup):
        self.S = CSeqList('S')  # [CGSPElement]
        self.F = CFrequentSetList('GSP.F',[CSeqList('F0')])
        C1 = self.init_pass(S)
        F1 = CSeqList('F1')
        for c in C1:
            if(c.calcSup(self.S) >= minsup):
                F1.append(c)
        self.F.append(F1)
        k = 2
        Fk_1 = F1
        while(Fk_1.__len__() > 0):
            Fk = CSeqList('F'+k.__str__())
            Ck = self.candidate_gen_SPM(Fk_1)
            for s in self.S:
                for c in Ck:
                    if c in s:
                        c.supCount += 1
            for c in Ck:
                if (c.calcSup(self.S) > minsup):
                    Fk.append(c)
            if Fk.__len__() > 0:
                self.F.append(Fk)
            Fk_1 = Fk
            k += 1

    def init_pass(self,S):
        itemDict = {} #name:CItem
        C1 = CSeqList('C1')
        for s in S:
            sequence = CSequence()
            isItemAppearedInSeqDict = {} #<{10},{10,20}>这种10只算一次supCount
            for ele in s:
                element = CGSPElement()
                for itm in ele:
                    if (itemDict.has_key(itm)):
                        ci = itemDict[itm]
                        if(not isItemAppearedInSeqDict.has_key(ci)):
                            ci.supCount += 1
                            isItemAppearedInSeqDict[ci] = 1
                    else:
                        ci = CItem(itm, 1)
                        itemDict[itm] = ci
                        isItemAppearedInSeqDict[ci] = 1
                    element.append(ci)
                element.sort()
                sequence.append(element)
            self.S.append(sequence)
        #gen 1-
        for itm in itemDict.values():
            C1.append(CSequence(CGSPElement(itm)))
        return C1

    def candidate_gen_SPM(self,Fk_1):
        if(Fk_1.__len__() == 0):
            return CTransList('C_null')
        i,j = 0,0
        k = Fk_1[0].itemCount() + 1
        Ck = CTransList('C'+str(k))
        for i in range(Fk_1.__len__()):
            s1 = Fk_1[i]
            for j in range(Fk_1.__len__()):
                if(i == j):
                    continue
                s2 = Fk_1[j]
                if k == 2:  # gen-C2:<{x}>,<{y}>  ---->  <{x.y}>,<{x},{y}>
                    ck = s1[:]
                    ck.extend(s2)
                    Ck.append(ck)
                    if(i<j):
                        ck = s1[:]
                        ck[0].extend(s2[0])
                        ck[0].sort()
                        Ck.append(ck)
                else:
                     #print 's1 s2',s1,s2
                     #print s1.getItemSequence(1, k - 1) , s2.getItemSequence(0, k - 2),s1.getItemSequence(1, k - 1) == s2.getItemSequence(0, k - 2)
                     if (s1.getItemSequence(1, k - 1) == s2.getItemSequence(0, k - 2)):
                        if (s2[s2.__len__() - 1].__len__() == 1):
                            ck = s1[:]
                            ck.append(s2[s2.__len__() - 1])
                        else:
                            ck = s1[:]
                            ck[ck.__len__() - 1].append(s2.getitem(s2.itemCount() - 1))
                            ck[ck.__len__() - 1].sort()
                        Ck.append(ck)
                        # 剪枝
                        for m in range(0, k):
                            ck_1 = ck[:].removeAt(m)
                            if not (ck_1 in Fk_1):
                                Ck.remove(ck)
                                break
        return Ck
