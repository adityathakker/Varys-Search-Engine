import os
from nltk.stem.porter import *
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import json
import unicodedata
import re

current_dir = os.getcwd()
files_dir = current_dir + "/Files/"


class Indexer:
    def __init__(self):
        print "\n++++++++ Indexer Bot ++++++++"
        print "+++++++++++++++++++++++++++++"

    def createIndex(self):
        stemmer = PorterStemmer()
        stopwords_list = stopwords.words('english')
        main_index = dict()
        for each_file in files_list:
            file_content = "\n".join(open(files_dir + each_file, "r").readlines())
            print "\tReading File: " + each_file
            file_content = unicodedata.normalize('NFKD', unicode(file_content, "utf-8")).encode('ascii', 'ignore')
            words_list = word_tokenize(file_content.lower())
            print "\tBreaking Into Words..."
            stemmed_word_list = [str(re.sub(r'\W+', '', stemmer.stem(each_word))) for each_word in words_list if
                                 each_word not in stopwords_list]
            # print stemmed_word_list
            print "\tFiltering Words..."
            print "\tAdding Each Filtered Word To Index..."
            for index, each_stemmed_word in enumerate(stemmed_word_list):
                if len(each_stemmed_word) > 0:
                    if each_stemmed_word not in main_index:
                        main_index.update({each_stemmed_word: dict()})
                    if each_file not in main_index[each_stemmed_word]:
                        main_index[each_stemmed_word].update({each_file: list()})
                    main_index[each_stemmed_word][each_file].append(index)

        print "\tIndexing Process Finished!\n"
        return main_index

    def saveIndex(self, index, indexName):
        print "\tSaving Index: " + indexName
        index_file = open(current_dir + "/Index/" + indexName, "w")
        index_file.write(str(index))
        index_file.close()
        print "\tIndex Has Been Saved!\n"

    def getSavedIndex(self, indexName):
        print "\tGetting Saved Index: " + indexName
        index_file = open(current_dir + "/Index/" + indexName, "r")
        string_index = "".join(index_file.readlines())
        json_acceptable_string_index = string_index.replace("'", "\"")
        dict_index = json.loads(json_acceptable_string_index)
        index_file.close()
        return dict_index
