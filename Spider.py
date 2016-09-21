from bs4 import BeautifulSoup
import requests
import os
import nltk
from nltk import PunktSentenceTokenizer
from CommonUtils import notify_message
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
    def __check_if_url_already_queued_or_crawled(db, url):
        url = url.encode('ascii', 'ignore')

        cursor = db.already_crawled.find({"url": url})
        if cursor.count() > 0:
            return cursor[0]["_id"]

        cursor = db.pending_for_crawling.find({"url": url})
        if cursor.count() > 0:
            return cursor[0]["_id"]

        return None

    @staticmethod
    def __insert_into_pending_for_crawling_urls_list(db, url):
        url = url.encode('ascii', 'ignore')

        result = db.pending_for_crawling.insert_one({"url": url})
        return result.inserted_id

    @staticmethod
    def __get_front_url_from_pending_for_crawling(db):
        documents = db.pending_for_crawling.find({})
        if documents.count() > 0:
            document = documents[0]
            db.pending_for_crawling.delete_one({"_id": document["_id"]})
            db.already_crawled.insert_one(document)
            return document["url"], document["_id"]
        else:
            return None, None

    @staticmethod
    def __remove_from_already_crawled(db, url_id):
        db.already_crawled.delete_one({"url": url_id})
        return

    @staticmethod
    def __index_content(url_id, db, soup):
        if soup.title is not None:
            try:
                title = str(soup.title.text).encode('ascii', 'ignore')
            except UnicodeEncodeError:
                title = unicode(soup.title.text, 'utf-8')
            if "-" in title:
                title = title[:title.find("-")]
        content = soup.find("div", {"id": "mw-content-text"}).text

        custom_tokenizer = PunktSentenceTokenizer()
        tokenized_sentences = custom_tokenizer.tokenize(unicode(content))

        page = dict()
        page["title"] = title
        hints_list = list()
        try:
            for sentence in tokenized_sentences:
                words = nltk.word_tokenize(sentence)
                tagged = nltk.pos_tag(words)

                grammar = r"""
        	          NP: {<DT|PP\$>?<JJ>*<NN>}   # chunk determiner/possessive, adjectives and noun
        	              {<NNP>+}                # chunk sequences of proper nouns
        	        """
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
        db.index_pages.insert_one(page)
        print(colored("\t\t\tInserted Into Indexed Pages", "yellow"))

        current_dir = os.getcwd()
        files_dir = current_dir + "/Originals/"
        file_name = url_id
        file_path = files_dir + str(file_name)
        created_file = open(file_path, "w")
        created_file.write(content.encode("utf-8"))
        created_file.close()
        print("\t\tOriginal Content Is Saved")
        return

    def __strip_links(self, current_url, urls_list, remove_external=False):
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

            url = url.encode('ascii', 'ignore')
            stripped_links.append(url)
        return stripped_links

    @staticmethod
    def __insert_into_reference(db, from_id, to_id):
        db.reference.insert_one({"from": from_id, "to": to_id})
        return

    def crawl_process(self):
        counter = 1

        client = MongoClient()
        db = client.varys

        headers = {'User-Agent': "Aditya's Browser"}

        if self.__check_if_url_already_queued_or_crawled(db, self.base_url) is None:
            self.__insert_into_pending_for_crawling_urls_list(db, self.base_url)
        crawling_url, url_id = self.__get_front_url_from_pending_for_crawling(db)

        while crawling_url is not None:
            print(colored("\t" + str(counter) + ". Crawling:  " + str(crawling_url)[:50] + "...", "yellow"))
            print(colored("\tURL ID: " + str(url_id), "white"))
            response = requests.get(crawling_url, headers=headers, verify=False)
            response_type = str(response.headers.get('content-type')).split(";")[0]
            if response_type == "application/atom+xml":
                print(colored("\t\tCannot Crawl An XML Page!", "red"))
                self.__remove_from_already_crawled(db, url_id)
            else:
                soup = BeautifulSoup(response.text, 'html.parser')

                self.__index_content(url_id, db, soup)
                print("\t\tIndexed '" + crawling_url[:50] + "...'")

                new_links = [link["href"] for link in soup.findAll("a", href=True)]
                new_links = self.__strip_links(crawling_url, new_links, remove_external=True)

                number_of_links = 0
                for each_link in new_links:
                    existing_id = self.__check_if_url_already_queued_or_crawled(db, each_link)
                    if existing_id is None:
                        new_id = self.__insert_into_pending_for_crawling_urls_list(db, each_link)
                        number_of_links += 1
                        self.__insert_into_reference(db, url_id, new_id)
                        # print(colored("\t\t\tNew Url Inserted '" + each_link + "...'", "blue"))
                    else:
                        self.__insert_into_reference(db, url_id, existing_id)
                        # print(colored("\t\t\tAlready Exists in Queue", "cyan"))

                print(colored("\t\t" + str(number_of_links) + " New Links Added", "yellow"))

            crawling_url, id_of_url = self.__get_front_url_from_pending_for_crawling(db)
            counter += 1
            print("")

            print("\tEntries In Pending URL's List: " + str(db.pending_for_crawling.find().count()))
            print("\tEntries In Already Crawled List: " + str(db.already_crawled.find().count()))

    def crawl(self):
        try:
            self.crawl_process()
        except KeyboardInterrupt as e:
            print(colored("\nExiting...", "red"))
            exit()
