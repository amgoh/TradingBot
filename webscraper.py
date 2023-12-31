import requests
import re
import urllib3
from googlesearch import search
from bs4 import BeautifulSoup
import nltk
import pickle

classifier_file = open("naivebayes.pickle", "rb")
classifier = pickle.load(classifier_file)
classifier_file.close()

headers = { 
    'User-Agent'      : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
    'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
    'Accept-Language' : 'en-US,en;q=0.5',
    'DNT'             : '1', # Do Not Track Request Header 
    'Connection'      : 'close'
}

def document_features(document, word_features):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains({})'.format(word)] = (word in document_words)
    return features

def predict_stock_opinion(stock, model):
    
    sentiments = []
    
    for i in search("latest news regarding the {} company".format(stock), tbs="qdr:d", num=10, stop=10, pause=3):
        try:
            print(i)
            
            page = requests.get(i, headers=headers, timeout=10)
            soup = BeautifulSoup(page.content, 'html5lib')
            
            words = ''
            article_tag = soup.find('article')
            if(article_tag != None):
                parapraph_tag = article_tag.find_all_next('p')
            else:
                paragraph_tag = soup.find_all('p')
            
            for i in paragraph_tag:
                words += " " + i.text
            
            all_words = nltk.FreqDist(w.lower() for w in words.split())
            word_features = list(all_words)[:2000]
            
            featureset = document_features(words.split(), word_features)
            sentiments.append(model.classify(featureset))
            
            
        except:
            continue
        
    if(sentiments.count("neg") > sentiments.count("pos")):
        return "neg"
    else:
        return "pos"