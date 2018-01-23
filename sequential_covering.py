#coding=utf-8
from common import *
from math import *

def test():
    '''
    this algorithm has not been tested yet,
    thus there might be something wrong with it
    :return:
    '''
    data = readdata('data/decisiontree.txt')
    clf = sequential_covering_1(data[1:], data[0],20,0.02)
    print clf.RuleList
    pass

class CRuleList(list):
    def __init__(self):
        '''
            just for print use
            '''
        list.__init__(self)

    def __str__(self):
        s = ''
        for rule in self:
            if rule[0].items().__len__() == 0:
                s += '[Default]'
            else:
                for item in rule[0].items():
                    s += item[0] + u'=' + item[1] + u','
                s = s.rstrip(u',')
            s += u'→{}\n'.format(rule[1])
        return s

class sequential_covering_1:
    def __init__(self,D,A,k,gainthreshold):
        '''
        sequential-covering-1 P60
        :param D: dataset(numpy.array)
        :param A: attribute_names(numpy.array)
        :param k: k of Beam search
        :param gainthreshold:when the gain of BestCond in D is
            greater than threshold,the BestCond will be employed.
            ps:gain can be understood as [entropy(D)-entropy(D')]
                where D' is subset of D covered by BestCond
        '''
        self.D = pd.DataFrame(D,columns=A)
        self.A = A[0:A.__len__() - 1]
        self.labelcolumn = A[-1]
        self.k = k
        self.threshold = gainthreshold
        self.RuleList = CRuleList()
        RuleList = self.RuleList
        Rule = self._learn_one_rule_1(self.D)
        D_ = self.D
        while Rule != None and self.D.__len__()>0:
            RuleList.append(Rule)
            D_ = self._removecoverdexamples(Rule[0], D_)
            Rule = self._learn_one_rule_1(D_)
        RuleList.append(({},self._majorityclass({},self.D)))

    def _removecoverdexamples(self, cond, D):
        '''
        remove the examples in D covered by cond
        :param cond: a condition
        :param D:Data set
        :return: the remaining examples
        '''
        D_ = D  # D'←the subset of training examples in D covered by BestCond
        for Ai in cond.keys():
            D_ = D_[D_[Ai] != cond[Ai]]
        return D_

    def _learn_one_rule_1(self,D):
        '''
        :param D: Data set
        :return: a best rule learned in D
            e.g.,A=1,B=3->Yes
        '''
        BestCond = {}
        candidateCondSet = [BestCond]
        #attributeValueParis<-the set of all attribute-value pairs in D of the form (Ai op v)
        #where Ai is attribute and v is a value or an interval
        attributeValuePairs = []
        for Ai in self.A:
            Vis = D[[Ai]].groupby(Ai).count().reset_index()
            for Vi in Vis.itertuples(index=False):
                attributeValuePairs.append((Ai,Vi[0]))
        while candidateCondSet.__len__() > 0:
            newCandidateCondSet = []
            for cond in candidateCondSet:
                for a in attributeValuePairs:
                    # remove duplicates and inconsistencies,e.g.,{Ai=v1,Ai=v2}
                    if not(cond.has_key(a[0])):
                        newCond = cond.copy()
                        newCond[a[0]] = a[1]
                        newCandidateCondSet.append(newCond)
            sortedNewCandidateCondSet = []
            for newCond in newCandidateCondSet:
                gain = self._evaluation(newCond,D) - self._evaluation(BestCond,D)
                sortedNewCandidateCondSet.append((newCond,gain))
                if(gain > 0):#evaluation(newCond,D) > evaluation(BestCond,D)
                    BestCond = newCond
            #candidateCondSet←the k best members of newCandidateCondSet according to
            #the results of the evaluation function
            sortedNewCandidateCondSet.sort(key=lambda x:x[1],reverse=True)
            k = 0
            candidateCondSet = []
            for cond_gain in sortedNewCandidateCondSet:
                candidateCondSet.append(cond_gain[0])
                k += 1
                if(k == self.k):
                    break
        if(self._evaluation(BestCond,D) - self._evaluation({},D) > self.threshold):
            return (BestCond,self._majorityclass(BestCond,D))
        else:
            return None

    def _cover(self,cond,D):
        '''
        :param cond: a condition
        :param D: Data set
        :return: the subset covered by cond
        '''
        D_ = D  # D'←the subset of training examples in D covered by BestCond
        for Ai in cond.keys():
            D_ = D_[D_[Ai] == cond[Ai]]
        return D_

    def _majorityclass(self,cond,D):
        '''
        :param cond: a condition
        :param D: Data set
        :return: the main(most frequent) class of D',where D' is
            a subset of D which is covered by cond
        '''
        D_ = self._cover(cond,D)
        Dx = D_[[self.labelcolumn]]
        Dx.insert(0, 'count', 0)
        Dx = Dx.groupby(self.labelcolumn).count().reset_index()
        Dx = Dx.max()
        return Dx[self.labelcolumn]

    def _evaluation(self,BestCond,D):
        '''
        :param BestCond: a condition
        :param D: Data set
        :return: (D')'s negative entropy,where D' is a subset
            of D covered by BestCond
        '''
        D_ = self._cover(BestCond,D)
        if(D_.__len__() == 0):#BestCond covers did't cover any example
            entropy = 1.0
        else:
            entropy = self._entropy(D_)
        return - entropy

    def _entropy(self,D_):
        '''
        :param D_: Data set
        :return: entroy(float)
        '''
        Dx = D_[[self.labelcolumn]]
        Dx.insert(0,'count',0)
        Dx = Dx.groupby(self.labelcolumn).count().reset_index()
        entropy = 0.0
        for row in Dx.itertuples(index=False):
            Prcj = float(row[1])/D_.__len__()
            entropy -= Prcj * log(Prcj,2)
        return entropy

