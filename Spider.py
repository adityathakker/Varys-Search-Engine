from bs4 import BeautifulSoup
import requests
import os
import nltk
import time
from nltk import PunktSentenceTokenizer
from urlparse import urljoin
from pymongo import MongoClient
from termcolor import colored


class Spider:
    base_url = str()

    def __init__(self, base_url):
        if base_url.endswith((".png", ".gif", ".jpg", ".pdf", ".css", ".js")):
            print(colored("\n\tInvalid URL! Cannot be Crawled!", "red"))
            exit()
        if base_url.endswith("/"):
            self.base_url = base_url[:len(base_url) - 1]
        else:
            self.base_url = base_url

        print(colored("\n++++++++ Spider Bot ++++++++", "yellow"))
        print(colored("+++++++++++++++++++++++++++++", "yellow"))

    @staticmethod
    def __check_if_url_is_known_url(db, url):
        url = url.encode('ascii', 'ignore')

        cursor = db.known_urls.find({"url": url})
        if cursor.count() > 0:
            return cursor[0]["_id"]

        return None

    @staticmethod
    def __insert_into_known_urls_as_pending(db, url):
        url = url.encode('ascii', 'ignore')
        result = db.known_urls.insert_one({"url": url, "score": 1.0, "status": "crawled"})
        return result.inserted_id

    @staticmethod
    def __get_front_url_from_pending_known_urls(db):
        documents = db.known_urls.find({"status": "crawled"})
        if documents.count() > 0:
            document = documents[0]
            db.known_urls.update_one(
                {
                    "_id": document["_id"]
                },
                {
                    "$set": {
                        "status": "indexed"
                    }
                }
            )
            return document["url"], document["_id"]
        else:
            return None, None

    @staticmethod
    def __remove_from_known_urls(db, url_id):
        db.knwon_urls.delete_one({"_id": url_id})
        return

    @staticmethod
    def __index_content(url_id, db, soup):
        if soup.title is not None:
            try:
                title = str(soup.title.text).encode('ascii', 'ignore')
            except UnicodeEncodeError:
                title = unicode(str(soup.title.text), 'utf-8')
            if "-" in title:
                title = title[:title.find("-")]
        # content = soup.find("div", {"id": "mw-content-text"}).text
        content = soup.text

        custom_tokenizer = PunktSentenceTokenizer()
        tokenized_sentences = custom_tokenizer.tokenize(unicode(content))

        page = dict()
        page["title"] = title
        hints_list = list()
        try:
            for sentence in tokenized_sentences:
                words = nltk.word_tokenize(sentence)
                tagged = nltk.pos_tag(words)

                grammar = r"""NP: {<DT|PP\$>?<JJ>*<NN>}
                {<NNP>+}"""
                chunk_parser = nltk.RegexpParser(grammar)
                chunked = chunk_parser.parse(tagged)
                for chunk in chunked.subtrees():
                    if chunk.label() == "NP":
                        line = list()
                        for each in chunk.leaves():
                            if len(each[0]) > 2:
                                line.append(each[0])
                        if len(line) > 0:
                            final_value = (" ".join(line)).lower()
                            hints_list.append(final_value)
                page["hints"] = hints_list

        except Exception as e:
            print(str(e))
        db.known_urls.update_one(
            {
                "_id": url_id
            },
            {
                "$set": {
                    "content": page
                }
            }
        )
        print(colored("\t\tUpdated With Indexed Content", "yellow"))

        # current_dir = os.getcwd()
        # files_dir = current_dir + "/Originals/"
        # file_name = url_id
        # file_path = files_dir + str(file_name)
        # created_file = open(file_path, "w")
        # created_file.write(content.encode("utf-8"))
        # created_file.close()
        # print("\t\tOriginal Content Is Saved")
        return

    def __strip_links(self, current_url, urls_list, remove_external=False):
        print(colored("\t\tRemoving Unwanted Links...", "yellow"))
        stripped_links = list()
        for url in urls_list:
            url = urljoin(current_url, url)
            if not url.startswith("http"):
                continue
            if url.endswith((".png", ".gif", ".jpg", ".pdf", ".css", ".js")):
                continue
            if remove_external and url[:len(self.base_url)] != self.base_url:
                continue
            if "#" in url:
                url = url[:url.index("#")]
            if "?" in url:
                url = url[:url.index("?")]
            if url.endswith("/"):
                url = url[:len(url) - 1]

            url = url.encode('ascii', 'ignore')
            if url not in stripped_links:
                stripped_links.append(url)
        return stripped_links

    # used to remove duplicate links
    @staticmethod
    def f7(seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    def __insert_into_referral_links(self, db, from_id, to_id):
        db.known_urls.update_one(
            {
                "_id": from_id
            },
            {
                "$push": {
                    "referral_links": to_id
                }
            }
        )

        document_from = db.known_urls.find({"_id": from_id})[0]
        document_to = db.known_urls.find({"_id": to_id})[0]
        new_score = document_to["score"] + (document_from["score"] * 0.00008)
        db.known_urls.update_one(
            {
                "_id": to_id
            },
            {
                "$set": {
                    "score": new_score
                }
            }
        )

        self.__update_scores(db, to_id, new_score, 0.00006)
        return

    def __update_scores(self, db, from_id, from_score, update_score_by):
        # print "Upating Scores By Ratio: " + str(update_score_by)
        if update_score_by <= 0.0:
            # print "returing"
            return

        # time.sleep(1)

        from_document = db.known_urls.find({"_id": from_id})[0]
        if "referral_links" in from_document:
            from_links = from_document["referral_links"]
            for each_link in from_links:
                original_doc = db.known_urls.find({"_id": each_link})[0]
                new_score = original_doc["score"] + (from_score * update_score_by)
                db.known_urls.update_one(
                    {
                        "_id": original_doc["_id"]
                    },
                    {
                        "$set": {
                            "score": new_score
                        }
                    }
                )
                self.__update_scores(db, original_doc["_id"], new_score, update_score_by - 0.00002)
        return

    def print_scores(self, db):
        docs = db.known_urls.find({}).sort([("score", 1)])
        for each_doc in docs:
            print(str(each_doc["url"]) + ":" + str(each_doc["score"]))

    def crawl_process(self):
        counter = 1

        client = MongoClient()
        db = client.varys

        headers = {'User-Agent': "Aditya's Browser"}

        if self.__check_if_url_is_known_url(db, self.base_url) is None:
            self.__insert_into_known_urls_as_pending(db, self.base_url)
        crawling_url, url_id = self.__get_front_url_from_pending_known_urls(db)
        while crawling_url is not None:
            print(colored("\t" + str(counter) + ". Crawling:  " + str(crawling_url)[:50] + "...", "yellow"))
            print(colored("\t\tURL ID: " + str(url_id), "white"))
            response = requests.get(crawling_url, headers=headers, verify=False)
            response_type = str(response.headers.get('content-type')).split(";")[0]
            if response_type == "application/atom+xml":
                print(colored("\t\tCannot Crawl An XML Page!", "red"))
                self.__remove_from_known_urls(db, url_id)
            else:
                soup = BeautifulSoup(response.text, 'html.parser')

                self.__index_content(url_id, db, soup)

                print(colored("\t\tGetting New Links...", "yellow"))
                new_links = [link["href"] for link in soup.findAll("a", href=True)]
                new_links = self.__strip_links(crawling_url, new_links, remove_external=True)

                print(colored("\t\tUpdating Scores...", "yellow"))
                number_of_links = 0
                for each_link in new_links:
                    existing_id = self.__check_if_url_is_known_url(db, each_link)
                    if existing_id is None:
                        new_id = self.__insert_into_known_urls_as_pending(db, each_link)
                        number_of_links += 1
                        self.__insert_into_referral_links(db, url_id, new_id)
                        # print(colored("\t\t\tNew Url Inserted '" + each_link + "...'", "blue"))
                    else:
                        self.__insert_into_referral_links(db, url_id, existing_id)
                        # print(colored("\t\t\tAlready Exists in Queue", "cyan"))

                print(colored("\t\t" + str(number_of_links) + " New Links Added", "yellow"))

            crawling_url, url_id = self.__get_front_url_from_pending_known_urls(db)
            counter += 1
            print("")

            print("\t\tEntries In Crawled List: " + str(db.known_urls.find({"status": "crawled"}).count()))
            print("\t\tEntries In Indexed List: " + str(db.known_urls.find({"status": "indexed"}).count()))
            # self.print_scores(db)

    def crawl(self):
        try:
            self.crawl_process()
        except KeyboardInterrupt as e:
            print(colored("\nExiting...", "red"))
            exit()
