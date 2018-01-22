#coding=utf-8
import urllib2
from sgmllib import SGMLParser
import uniout
from BeautifulSoup import BeautifulSoup
import os
import re
import jieba
import chardet
from sklearn.datasets.base import Bunch
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer,TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import hashlib
import numpy as np

def test():
    fpath = 'train_urls/'
    #fpath += 'littlegame.txt'
    #fpath += 'game.txt'
    #fpath += 'avd.txt'
    fpath += 'material.txt'
    testURLs = file(fpath).read().split(u'\n')
    DMCrawler(testURLs)

class DMCrawler():
    '''
    this is a web page crawler who crawls the pages similiar with input page
    '''
    def __init__(self, trainURLSet):
        CCrawledPage.init()
        train_page_set = []
        for url in trainURLSet:
            page = CCrawledPage(url)
            if page.succeed:
                train_page_set.append(page)
            CCrawledPage.CrawledUrlDict[url] = 1
        #build tfidf array
        clf = CNBClassifier(CTF_IDF(train_page_set))
        crawledpagelist = []
        whitePage = CCrawledPage('null')
        whitePage.join(train_page_set)
        whitePage.crawl(15,crawledpagelist,clf,120)
        crawledpagelist.sort(key=lambda x:x.likelihood,reverse=True)
        top = 20
        for page in crawledpagelist:
            print page.url ,page.likelihood ,page.label
            if(top > 0):
                top -= 1
            else:
                break

class CNBClassifier(MultinomialNB):
    def __init__(self, trainTF_IDF):
        MultinomialNB.__init__(self,alpha=0.001)
        MultinomialNB.fit(self, trainTF_IDF.tfidf, trainTF_IDF.label)
        self.trainTF_IDF = trainTF_IDF
        pass

    def predict_mostlike(self,crawledPage):
        cdm = CTF_IDF([crawledPage], self.trainTF_IDF.vocabulary)
        c = MultinomialNB.predict(self, cdm.tfidf)
        jll = self._joint_log_likelihood(cdm.tfidf)
        #smaller the number is,the more similar the document
        p = int(jll[0].min()) * -1
        return c[0],p

class CTF_IDF():
    def __init__(self,pagelist,vocabulary = None):
        corpus = []
        self.label = []
        for page in pagelist:
            self.label.append(page.title)
            corpus.append(page.words_seg)
        vectorizer = TfidfVectorizer(sublinear_tf=True,max_df=0.5,vocabulary=vocabulary)
        self.tfidf = vectorizer.fit_transform(corpus)
        self.vocabulary = vectorizer.get_feature_names()
        pass

    def __str__(self):
        weight = self.tfidf.toarray()
        word = self.vocabulary
        sl = []
        s = u''
        for i in range(len(weight)):  # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
            s += u'-------这里输出第", i, u"类文本的词语tf-idf权重------\n'
            for j in range(len(word)):
                s += word[j] + str(weight[i][j]) + u'\n'
        return s


class CCrawledPage(SGMLParser):
    StopWordsDict = {}
    for word in file('hlt_stop_words.txt').read().split(u'\n'): #少了u' '就会出现编码，因为'\n'会是a part of a unicode char
        StopWordsDict[word] = 1
    CrawledUrlDict = {}
    UrlPattern = re.compile(r'(http://[^/]+)', re.IGNORECASE)
    DominPattern = re.compile(r'([^\.]+)\.[^\.]+$')
    @staticmethod
    def init():
        CCrawledPage.CrawledUrlDict = {}

    def __init__(self,url):
        SGMLParser.__init__(self)
        self.url = url
        self.urls = []
        self.content = ''
        self.valid_content = True
        self.dist = 0
        self.succeed = True
        self.title = 'Default'
        self.label = 'Null'
        self.domin = ''
        if(url == 'null'):
            return
        else:
            self.domin = self.DominPattern.search(url).group(1)
        try:
            CCrawledPage.CrawledUrlDict[self.domin] = 1
            print 'downloading:{},'.format(self.url),
            m2 = hashlib.md5()
            m2.update(url)
            fname = 'pages/' + m2.hexdigest()
            if(os.path.exists(fname)):
                content = file(fname).read()
            else:
                content = urllib2.urlopen(self.url, timeout=3).read()
                #file(fname,'w').write(content)
            print 'succeed!'
        except:
            print 'failed!'
            self.succeed = False
            return
        self.encoding = chardet.detect(content)['encoding']
        if(self.encoding == None):
            self.succeed = False
            return
        try:
            self.feed(content)
        except:
            self.succeed = False
            return
        #convert content into word list
        wordSet = jieba.cut(self.content)
        wordList = []
        for word in wordSet:
            if(self.StopWordsDict.has_key(word)):
                continue
            else:
                wordList.append(word)
        self.words_seg = ' '.join([word for word in wordList])

    def distance(self,page):
        return 1

    def crawl(self, deepth, crawledpagelist,classifier,minlikelihood=0):#DFS crawl
        queue = []
        #enqueue
        queue = self.urls
        while(deepth>0):
            url = queue[0]
            page = CCrawledPage(url)
            queue.remove(url) #dequeue
            if page.succeed:
                page.label,page.likelihood = classifier.predict_mostlike(page)
                print page.url, ' --- likilihood:', page.likelihood, ' --- label:', page.label
                if (page.likelihood > minlikelihood):
                    crawledpagelist.append(page)
                    queue.extend(page.urls) #enqueue
                    deepth -= 1

    def start_title(self,attrs):
        self.title = 'title'

    def start_a(self,attrs):
        for attr in attrs:
            #get friend URL
            if(attr[0] == 'href'):
                match = self.UrlPattern.search(attr[1])
                if match != None:
                    url = match.group(1)
                    domin = self.DominPattern.search(url).group(1)
                    if not CCrawledPage.CrawledUrlDict.has_key(domin):
                        self.urls.append(url)
                        CCrawledPage.CrawledUrlDict[domin] = 1
                return

    def start_script(self,attrs):
        self.valid_content = False

    def end_script(self):
        self.valid_content = True

    def handle_data(self, data):
        if self.valid_content:
            data = data.decode(self.encoding,'ignore').encode('utf-8')
            data = re.sub('\s', '', data)
            if(data.__len__() > 1):
                self.content += data
                if(self.title == 'title'):
                    self.title = data

    def __str__(self):
        s = ''
        for url in self.urls:
            s += url + '\n'

        s += self.content

        return s

    def join(self,pageList):
        for page in pageList:
            self.urls.extend(page.urls)
        return self

