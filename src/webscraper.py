import requests
from googlesearch import search
from bs4 import BeautifulSoup
import nltk

headers = { 
    'User-Agent'      : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
    'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
    'Accept-Language' : 'en-US,en;q=0.5',
    'DNT'             : '1', # Do Not Track Request Header 
    'Connection'      : 'close'
}

def document_features(document, word_features):
    """
    Returns a dict of features, featureset, that can be used to classify a list of words
    """
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains({})'.format(word)] = (word in document_words)
    return features

def update_owned_stock_opinion(stock, model):
    return

def predict_stock_opinion(stock, model):
    """
    Returns the sentiment of the specified publicly traded company based on the top 10 news articles from a Google search from the last 2 days
    
    Parameters:
        stock - the name of the publicly traded company\n
        model - a NaiveBayesClassifier used for sentiment analysis of the queried news articles
    
    Returns:
        A string, either 'neg' or 'pos' representing the perceived sentiment
    """
    sentiments = [] # list of all sentiments from all scraped articles
    
    for i in search("latest news regarding the {} company".format(stock), tbs="qdr:2d", num=10, stop=10, pause=3):
        try:
            page = requests.get(i, headers=headers, timeout=10) # access webpage, stop if loading exceeds 10 seconds
            soup = BeautifulSoup(page.content, 'html5lib') # parse HTML
            
            
            # gather all words from the article
            words = ''
            article_tag = soup.find('article')
            if(article_tag != None):
                parapraph_tag = article_tag.find_all_next('p')
            else:
                paragraph_tag = soup.find_all('p')
            
            for i in paragraph_tag:
                words += " " + i.text
            
            # create a featureset and classify it using the NaiveBayesClassifier model
            all_words = nltk.FreqDist(w.lower() for w in words.split())
            word_features = list(all_words)[:2000]
            
            featureset = document_features(words.split(), word_features)
            sentiments.append(model.classify(featureset))
            
            
        except:
            # catch exceptions, in case of an error accessing a webpage
            continue
        
    # check if more negative sentiment
    if(sentiments.count("neg") > sentiments.count("pos")):
        return "neg"
    # otherwise return positive sentiment, if equal, assume positive
    else:
        return "pos"