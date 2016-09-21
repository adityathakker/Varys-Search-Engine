from Spider import Spider
from Query import Query
import sys

arguments = sys.argv
if arguments[1] == "crawl":
    spider = Spider("https://en.wikipedia.org/")
    spider.crawl()
elif arguments[1] == "query":
    query = Query(arguments[2])
    query.query()
# # query.multiWordQuery(["action","design"])
