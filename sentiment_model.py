import nltk
from nltk.corpus import movie_reviews
import random
import pickle
from tqdm import tqdm

documents = [(list(movie_reviews.words(fileid)), category)
              for category in movie_reviews.categories()
              for fileid in movie_reviews.fileids(category)]

for c in movie_reviews.categories():
    print(c)

random.shuffle(documents)

# Define the feature extractor
all_words = nltk.FreqDist(w.lower() for w in movie_reviews.words())
word_features = list(all_words)[:2000]

def document_features(document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains({})'.format(word)] = (word in document_words)
    return features

# Train Naive Bayes classifier
featuresets = [(document_features(d), c) for (d,c) in documents]
train_set, test_set = featuresets[1000:], featuresets[:1000]

classifier = open("naivebayes.pickle", "rb")
model = pickle.load(classifier)
classifier.close()

for epoch in tqdm(range(200)):
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    if(nltk.classify.accuracy(classifier, test_set) > nltk.classify.accuracy(model, test_set)):
        model = classifier   

save_classifier = open("naivebayes.pickle","wb")
pickle.dump(model, save_classifier)
save_classifier.close()


print(nltk.classify.accuracy(model, test_set))