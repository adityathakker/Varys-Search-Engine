from bs4 import BeautifulSoup
import requests
import os
from os import listdir
from os.path import isfile, join
import MySQLdb


class Crawler:
    current_dir = os.getcwd()
    files_dir = current_dir + "/Files/"
    base_url = str()

    def __init__(self, base_url):
        if base_url.endswith((".png", ".gif", ".jpg", ".pdf", ".css", ".js")):
            print("Invalid URL! Cannot be Crawled!")
            exit()
        if not base_url.endswith("/"):
            self.base_url = base_url + "/"
        else:
            self.base_url = base_url

        print("\n++++++++ Crawler Bot ++++++++")
        print("+++++++++++++++++++++++++++++")

    # def printList(lists):
    # 	for item in lists:
    # 		print item

    def get_all_files_list(self):
        files_list = [f for f in listdir(self.files_dir) if (isfile(join(self.files_dir, f)) and not f.endswith("~"))]
        return files_list

    @staticmethod
    def strip_html(soup):
        for tag in soup.findAll("style"):
            tag.replaceWith("")
        for tag in soup.findAll("script"):
            tag.replaceWith("")
        for tag in soup.findAll("footer"):
            tag.replaceWith("")
        for tag in soup.findAll("nav"):
            tag.replaceWith("")
        for tag in soup.findAll("header"):
            tag.replaceWith("")

        final_content = list()
        for each_line in soup.getText().splitlines():
            if len(each_line) > 0:
                final_content.append(each_line.strip())
        return "\n".join(final_content)

    def strip_links(self, urls_list, remove_external=False):
        stripped_links = list()
        for url in urls_list:
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

            stripped_links.append(url)
        return stripped_links

    def insert_into_pending_urls_list(self, db, cursor, url):
        sql_insert = """INSERT INTO pending_crawling_links(link)
                         VALUES ('""" + url + """')"""
        try:
            cursor.execute(sql_insert)
            db.commit()
        except:
            db.rollback()

    def get_single_url_from_pending_list(self, db, cursor):
        sql_select = """select id, link from pending_crawling_links limit 1"""
        try:
            cursor.execute(sql_select)
            result = cursor.fetchone()
            url = result[1]
            cursor.execute("delete from pending_crawling_links where id=" + result[0])
            db.commit()
            return url
        except:
            db.rollback()
            return None

    def crawl(self):
        db = MySQLdb.connect("localhost", "root", "", "arya")
        cursor = db.cursor()

        # all_links = [self.base_url]
        self.insert_into_pending_urls_list(self, db, cursor, self.base_url)
        print("\tCrawling Process Started...")

        url = self.get_single_url_from_pending_list(self, db, cursor)
        while (url != None):
            print("\tCrawling:  " + url)
            headers = {'User-Agent': "Aditya's Browser"}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response, 'html.parser')
            new_links = [link["href"] for link in soup.findAll("a", href=True)]
            new_links = self.strip_links(new_links, remove_external=True)
            for link in new_links:
                if link not in all_links:
                    all_links.append(link)

            content = self.strip_html(soup)

            files_list = self.get_all_files_list()
            file_name = url.replace("/", "\\")
            file_path = self.files_dir + file_name
            if file_name not in files_list:
                created_file = open(file_path, "w")
                created_file.write(content.encode("ascii", "ignore"))
                created_file.close()
            else:
                print("\tAlready Indexed!")
            url = self.get_single_url_from_pending_list(self, db, cursor)

        # for url in all_links:
        #     print("\tCrawling:  " + url)
        #     headers = {'User-Agent': "Aditya's Browser"}
        #     response = requests.get(url, headers=headers)
        #     soup = BeautifulSoup(response, 'html.parser')
        #     new_links = [link["href"] for link in soup.findAll("a", href=True)]
        #     new_links = self.strip_links(new_links, remove_external=True)
        #     for link in new_links:
        #         if link not in all_links:
        #             all_links.append(link)
        #
        #     content = self.strip_html(soup)
        #
        #     files_list = self.get_all_files_list()
        #     file_name = url.replace("/", "\\")
        #     file_path = self.files_dir + file_name
        #     if file_name not in files_list:
        #         created_file = open(file_path, "w")
        #         created_file.write(content.encode("ascii", "ignore"))
        #         created_file.close()
        #     else:
        #         print("\tAlready Indexed!")

        print("\tCrawling Process Finished!\n")
        db.close()

        # printList(all_links)
