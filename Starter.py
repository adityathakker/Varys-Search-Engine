import os
from os import listdir
from os.path import isfile, join
from Indexer import Indexer
from Query import Query
from Crawler import Crawler


def get_all_files_list():
    current_dir = os.getcwd()
    files_dir = current_dir + "/Files/"
    files_list = [f for f in listdir(files_dir) if (isfile(join(files_dir, f)) and not f.endswith("~"))]
    return files_list


crawler = Crawler("http://greatist.com/")
crawler.crawl()

# crawler = Crawler("http://www.android4devs.com/")
# crawler.crawl()


# indexer = Indexer()
# # index = indexer.createIndex(getAllFilesList())
# # indexer.saveIndex(index,"android-hive")
# index = indexer.getSavedIndex("android-hive")

# query = Query(index)
# query.oneWordQuery("intent")
# # query.multiWordQuery(["action","design"])
