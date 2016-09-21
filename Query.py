from pymongo import MongoClient
from termcolor import colored


class Query:
    query_words_list = list()

    def __init__(self, query):
        self.query_words_list = query.split()

        new_query = list()
        for each in self.query_words_list:
            new_query.append({"hints" : {'$regex': '.*' + each + '.*'}})

        self.query_words_list = new_query

        print(colored("\n++++++++ Queryer Bot ++++++++", "yellow"))
        print(colored("++++++++++++++++++++++++++++++", "yellow"))

    def query(self):
        client = MongoClient()
        db = client.varys

        cursor = db.index_pages.find({'$and': self.query_words_list})
        for document in cursor:
            print(document["title"])
