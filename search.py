
# coding: utf-8

# In[9]:


# import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import xml.etree.ElementTree as ET
import re                                                           
from collections import defaultdict
from Stemmer import Stemmer
import time
import os
import gc
from heapq import heappush, heappop
import sys
from math import log10
from pympler.asizeof import asizeof


# In[3]:


stop_words = set(stopwords.words('english'))
def stopWords(listOfWords):                                         #Stop Words Removal
    temp=[key for key in listOfWords if key not in stop_words]
    return temp

ps = Stemmer("english")

def myTokenizer(text):
    words = re.split(r'(\b[^-\s]+\b)((?<=\.\w).)?', text)
    tok = [i for i in words if i!=None and i != " " and i != ""]
    tok = [ word.lower() for word in tok if re.match('^[a-zA-Z0-9\'-.]+$',word) and not re.match('^[\',-_]+$',word) and not re.match('^[^\w]+$',word)]
    fin_tok = []
    for t in tok:
        fin_tok.append(re.sub("[\+*=&$@/(),.\-!?:]+", '', t))
    fin_tok = [i for i in fin_tok if i!=None and i != " " and i != ""]
    return fin_tok

def processText(text):
    # tokenization
    fin_tok = myTokenizer(text)
    
    # StopWord removal 
    fin_tok = stopWords(fin_tok)
    
    #Stemming
    fin_tok = map(ps.stemWord, fin_tok)
    
    # Final processing
    tok = []
    for t in fin_tok:
        tok.append(re.sub("[']+", '', t))
    return tok


# In[35]:


secIndPath = "final_index/secInverIndex.txt"
topicMapPath = "titleMap.txt"
inverIndPath = "final_index/"
bodyP = "b.txt"
titleP = "t.txt"
categP = "c.txt"
extP = "e.txt"
infoP = "i.txt"
totalDoc = 8532000

def TF(num):
    return log10(1.0 + float(num))

def IDF(num):
    return log10(totalDoc/float(num))

did = {}
with open(topicMapPath,'r') as fil:
    line = fil.readline()
    while line:
        line = line.rstrip(" \n")
        line = line.split(":")
        did[line[0]] = line[1]
        line = fil.readline()


# In[36]:


wordPos = {}
secIndPnt = open(secIndPath, "r")
line = secIndPnt.readline()
while line:
    line = line.split(":")
    offset = int(line[1].rstrip("\n"))
    wordPos[line[0]] = offset
    line = secIndPnt.readline()
secIndPnt.close()    


# In[100]:


inverIndPnt = open(inverIndPath + bodyP,"r")

def findRel(tokens):
    topk = []
    docs = []
    post = defaultdict(list)
#     sz   = defaultdict(int)
    np = {}
    for i,tok in enumerate(tokens):
        offset = wordPos[tok]
        inverIndPnt.seek(offset, 0)
        pList = inverIndPnt.readline().partition("|")[2]
        post[i] = pList.split("|")
#         sz[i] = len(pList)
        cont = post[i][0].split(":")
        cont.append(i)
        heappush(docs, cont)
        np[i] = 1
        
    did, freq, tok = heappop(docs)
    score = TF(freq)*IDF(len(post[tok]))
    if np[tok] < len(post[tok]):
        cont = post[tok][np[tok]].split(":")
        cont.append(tok)
        heappush(docs, cont)
        np[tok] += 1

    if len(tokens) > 1:
        ndid, nfreq, ntok = heappop(docs)
    else:
        ndid = -1
    fl = 1
    while fl:
        fl = 0
        while docs:
            if did != ndid:
                heappush(topk, [score, did])
                did, tok, freq = ndid, ntok, nfreq
                score = TF(freq)*IDF(len(post[tok]))
                if len(topk) > 10:
                    waste = heappop(topk)
            else:
                score += TF(nfreq)*IDF(len(post[tok]))
                if np[ntok] < len(post[tok]):
                    cont = post[ntok][np[ntok]].split(":")
                    cont.append(ntok)
                    heappush(docs, cont)
                    np[ntok] += 1
            ndid, nfreq, ntok = heappop(docs)
            if did == -1:
                did, freq, tok = heappop(docs)
        for tok,i in enumerate(tokens):
            if np[tok] < len(post[tok]):
                cont = post[tok][np[tok]].split(":")
                cont.append(tok)
                heappush(docs, cont)
                np[tok] += 1
                fl = 1
    return topk

def fieldQ(f, tokens):
    topk = []
    docs = []
    post = defaultdict(list)
    np = {}
    fil = open(inverIndPath + f + ".txt", "r")
    for i,tok in enumerate(sorted(tokens)):
        line = fil.readline()
        while line:
            temp = line.partition("|")
            tokP = temp[0]
            if tokP == tok:
                pList = temp[2]
                post[i] = pList.split("|")
                cont = post[i][0].split(":")
                cont.append(i)
                heappush(docs, cont)
                np[i] = 1
                break
            else:
                line = fil.readline()
        
    did, freq, tok = heappop(docs)
    score = TF(freq)*IDF(len(post[tok]))
    if np[tok] < len(post[tok]):
        cont = post[tok][np[tok]].split(":")
        cont.append(tok)
        heappush(docs, cont)
        np[tok] += 1

    if len(tokens) > 1:
        ndid, nfreq, ntok = heappop(docs)
    else:
        ndid = -1
    fl = 1
    while fl:
        fl = 0
        while docs:
            if did != ndid:
                heappush(topk, [score, did])
                did, tok, freq = ndid, ntok, nfreq
                score = TF(freq)*IDF(len(post[tok]))
                if len(topk) > 10:
                    waste = heappop(topk)
            else:
                score += TF(nfreq)*IDF(len(post[tok]))
                if np[ntok] < len(post[tok]):
                    cont = post[ntok][np[ntok]].split(":")
                    cont.append(ntok)
                    heappush(docs, cont)
                    np[ntok] += 1
            ndid, nfreq, ntok = heappop(docs)
            if did == -1:
                did, freq, tok = heappop(docs)
        for tok,i in enumerate(tokens):
            if np[tok] < len(post[tok]):
                cont = post[tok][np[tok]].split(":")
                cont.append(tok)
                heappush(docs, cont)
                np[tok] += 1
                fl = 1
    return topk
    
def handleField(query):
    fq = query.split(";")
    res = []
    for q in fq:
        f, query = q.split(":")
        qtok = processText(query)
        if f == "b":
            docs = findRel(qtok)
        else:
            docs = fieldQ(f,qtok)
        res += docs
    res = map(int, [doc for sc, doc in sorted(res, reverse=True)])
    return res
    
    
    
def search(query):
    if re.search(r'[t|b|c|e|i]:',query[:2]):
        docs = handleField(query)
    else: 
        qtok = processText(query)
        docs = findRel(qtok)
        docs = map(int, [doc for sc, doc in sorted(docs, reverse=True)])
    return docs

def mapTitle(docs):
    return [did[doc] for doc in docs]

print search("t:hello world")  
    

