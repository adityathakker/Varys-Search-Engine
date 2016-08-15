import os
from Ranker import TFIDF
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.tokenize import word_tokenize

current_dir = os.getcwd()
files_dir = current_dir + "/Files/"


class Query:
    index = dict()

    def __init__(self, index):
        self.index = index
        print "\n+++++++++ Query Bot +++++++++"
        print "+++++++++++++++++++++++++++++"

    def printListOfTuples(self, listOfTuples):
        i = 1;
        for item in listOfTuples:
            print "\t" + (str(i) + ". " + item[0] + " (" + str(item[1]) + ")").replace("\\", "/")
            i += 1

    def oneWordQuery(self, word, limit=10):
        print "\tQuerying \"" + word + "\" against the index"
        if word in self.index:
            tf_idf_ranker = TFIDF(self.index[word])
            ranked_list = tf_idf_ranker.rankIt()
            print "\tRanking The Fetched Result..."
            self.printListOfTuples(ranked_list[:limit])
        else:
            print "Oops! Not Such Word Found!"

    def multiWordQuery(self, words):
        print "\tQuerying " + ",".join(words) + " against the index"
        tempIndex = dict()
        for word in words:
            if word in self.index:
                for key, value in self.index[word].items():
                    if key in tempIndex:
                        tempIndex[key] = tempIndex[key] + value
                    else:
                        tempIndex[key] = value

        tf_idf_ranker = TFIDF(tempIndex)
        ranked_list = tf_idf_ranker.rankIt()
        print "\tRanking The Fetched Result..."
        self.printListOfTuples(ranked_list)
