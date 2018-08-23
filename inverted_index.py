
# coding: utf-8

# In[38]:


# import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import xml.etree.ElementTree as ET
import re                                                           
from collections import defaultdict
# from nltk.stem import PorterStemmer
from Stemmer import Stemmer
import time

def my_tokenizer(text):
    words = re.split(r'(\b[^\s]+\b)((?<=\.\w).)?', text)
    tok = [i for i in words if i!=None and i != " " and i != ""]
    tok = [ word.lower() for word in tok if re.match('^[a-zA-Z0-9\'-.]+$',word) and not re.match('^[0-9_]+$',word)]
    return tok


ps = Stemmer("english")

# ps = PorterStemmer()
stop_words = set(stopwords.words('english'))

def strip_tag_name(t):
    t = elem.tag
    idx = k = t.rfind("}")
    if idx != -1:
        t = t[idx + 1:]
    return t

def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)

def stopWords(listOfWords):                                         #Stop Words Removal
    temp=[key for key in listOfWords if key not in stop_words]
    return temp


# In[39]:


def findInfoBoxTextCategory(data):                                        #find InfoBox, Text and Category
    info=[]
    bodyText=[]
    category=[]
    links=[]
    flagtext=1
    lines = data.split('\n')
    for i in xrange(len(lines)):
        if '{{infobox' in lines[i]:
            flag=0
            temp=lines[i].split('{{infobox')[1:]
            info.extend(temp)
            while True:
                if '{{' in lines[i]:
                    count=lines[i].count('{{')
                    flag+=count
                if '}}' in lines[i]:
                    count=lines[i].count('}}')
                    flag-=count
                if flag<=0:
                    break
                i+=1
                info.append(lines[i])

        elif flagtext:
            if '[[category' in lines[i] or '==external links==' in lines[i]:
                flagtext=0
            bodyText.append(lines[i])
            
    else:
        if "[[category" in lines[i]:
            line = data.split("[[category:")
            if len(line)>1:
                category.extend(line[1:-1])
                temp=line[-1].split(']]')
                category.append(temp[0])

    category = my_tokenizer(' '.join(category))
    category = stopWords(category)
    category = map(ps.stemWord, category)

    info = my_tokenizer(' '.join(info))
    info = stopWords(info)
    info = map(ps.stemWord,info)

    bodyText = my_tokenizer(' '.join(bodyText))
    bodyText = stopWords(bodyText)
    bodyText = map(ps.stemWord, bodyText)

    infobox = defaultdict(int)
    for key in info:
        infobox[key] += 1

    bodyTxt = defaultdict(int)
    for key in bodyText:
        bodyTxt[key] += 1

    categ = defaultdict(int)
    for key in category:
        categ[key] += 1
  
    return infobox, bodyTxt, categ


# In[40]:


def create_index(title, text):
    twords = my_tokenizer(title)
    twords = stopWords(twords)
    twords = map(ps.stemWord, twords)
    
    ttokens = defaultdict(int)
    for key in twords:
        ttokens[key]+=1
    info, bodyText, category = findInfoBoxTextCategory(text)
    return ttokens, bodyText, info, category


# In[42]:


dumpPath = 'wiki-search-small.xml'
# dumpPath = 'test.xml'

start_time = time.time()
totalCount = 0
temp = -1
inver = defaultdict(str)
for event, elem in ET.iterparse(dumpPath, events=('start', 'end')):
    tname = strip_tag_name(elem.tag)
    if event == 'start':
        if tname == 'page':
            title = ''
            did = -1
            redirect = ''
            inrevision = False
            ns = 0
            text = ''
        elif tname == 'revision':
            # Do not pick up on revision id's
            inrevision = True
    else:
        if tname == 'title':
            title = elem.text
        elif tname == 'id' and not inrevision:
            did = int(elem.text)
        elif tname == 'redirect':
            redirect = elem.attrib['title']
        elif tname == 'ns':
            ns = int(elem.text)
        elif tname == 'text':
            text = elem.text
        elif tname == 'page':
            if redirect == "":
                redirect = title
            ttoken, body, tinfo, tcat = create_index(redirect,text)
            for keys in set(ttoken.keys() + body.keys() + tinfo.keys()):
                inver[keys] += "|" + str(did)
                if keys in ttoken:
                    inver[keys] += "t" + str(ttoken[keys])
                if keys in body:
                    inver[keys] += "b" + str(body[keys])
                if keys in tinfo:
                    inver[keys] += "i" + str(tinfo[keys])
                if keys in tcat:
                    inver[keys] += "c" + str(tcat[keys])
            totalCount += 1
        elem.clear()
#         if (totalCount%100 == 0 and totalCount != temp):
#             temp = totalCount
#             print totalCount
# for keys in inver:
#     print keys,inver[keys]
with open('invertedIndex.txt', 'w') as fil:
    for key in inver:
        fil.write(key.encode('ascii', 'ignore').decode('ascii') + inver[key] + "\n")

elapsed_time = time.time() - start_time
print("Elapsed time: {}".format(hms_string(elapsed_time)))
# print totalCount

