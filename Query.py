from pymongo import MongoClient
from termcolor import colored


class Query:
    query_words_list = list()

    def __init__(self, query):
        self.query_words_list = query.split()

        new_query = list()
        for each in self.query_words_list:
            new_query.append({"content.hints": {'$regex': '.*' + each + '.*'}})

        self.query_words_list = new_query

        print(colored("\n++++++++ Queryer Bot ++++++++", "yellow"))
        print(colored("++++++++++++++++++++++++++++++", "yellow"))

    def query(self):
        client = MongoClient()
        db = client.varys

        cursor = db.known_urls.find(
            {
                "status": "indexed",
                "$and": self.query_words_list
            }
        ).sort([("score", -1)])
        for document in cursor:
            print(document["content"]["title"] + " " + str(document["score"]))
