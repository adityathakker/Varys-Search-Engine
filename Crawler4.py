from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
from CommonUtils import notify_message
from urlparse import urljoin

class Crawler:
    base_url = str()

    def __init__(self, base_url):
        if base_url.endswith((".png", ".gif", ".jpg", ".pdf", ".css", ".js")):
            print("\n\tInvalid URL! Cannot be Crawled!")
            exit()
        if base_url.endswith("/"):
            self.base_url = base_url[:len(base_url)-1]
        else:
            self.base_url = base_url

        print("\n++++++++ Crawler Bot ++++++++")
        print("+++++++++++++++++++++++++++++")

    def insert_into_pending_urls_list(self, db, cursor, url):
        url = url.encode('ascii', 'ignore')
        sql_insert = """INSERT INTO pending_crawling_links(link)
                         VALUES ('""" + url + """')"""
        try:
            cursor.execute(sql_insert)
            db.commit()
            return cursor.lastrowid
        except Exception, e:
            notify_message("Exception in 'insert_into_pending_urls_list'", e, "Sql: " + sql_insert)
            db.rollback()
            return None

    def strip_html(self, soup):
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

    def strip_links(self, current_url, urls_list, remove_external=False):
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

    def check_if_url_already_queued_or_crawled(self, cursor, url):
        url = url.encode('ascii', 'ignore')
        sql_check_if_exists = """select new.id, new.link from
        (select id, link from pending_crawling_links union select id, link from already_crawled_links) as new
         where link='""" + url + """'"""
        # print(sql_check_if_exists)
        try:
            cursor.execute(sql_check_if_exists)
            if cursor.rowcount > 0:
                result = cursor.fetchone()
                return result[0]
            else:
                return -1
        except Exception, e:
            notify_message("Exception in 'check_if_url_already_queued_or_crawled'", e, "SQL: " + sql_check_if_exists)
            return -1

    def get_front_url_from_pending_urls_list(self, db, cursor):
        sql_select = """select id, link from pending_crawling_links order by time_of_insertion limit 1"""
        try:
            cursor.execute(sql_select)
            if cursor.rowcount > 0:
                result = cursor.fetchone()
                crawling_url = result[1]
                id_of_url = result[0]
                sql_delete_from_pending_links = """delete from pending_crawling_links where id=""" + str(id_of_url)
                cursor.execute(sql_delete_from_pending_links)
                sql_insert_into_already_crawled = "insert into already_crawled_links(id, link) " \
                                                  "values(""" + str(id_of_url) + """,'""" + crawling_url + """')"""
                cursor.execute(sql_insert_into_already_crawled)
                db.commit()
                return crawling_url, id_of_url
            else:
                print("\n\tQueue is Empty!")
                return None, None
        except Exception, e:
            notify_message("Exception in 'get_front_url_from_pending_urls_list'", e, "SQL: " + sql_select)
            db.rollback()
            return None, None

    def insert_into_reference(self, db, cursor, from_id, to_id):
        sql_insert_reference = """insert into reference_linking values(""" + str(from_id) + """, """ + str(
            to_id) + """)"""
        try:
            cursor.execute(sql_insert_reference)
            db.commit()
        except Exception, e:
            notify_message("Exception in 'insert_into_reference'", e, "SQL: " + sql_insert_reference)
            db.rollback()

    def remove_from_already_crawled(self, db, cursor, id_of_link):
        sql_remove_from_already_crawled = """ delete from already_crawled_links where id=""" + str(id_of_link)
        try:
            cursor.execute(sql_remove_from_already_crawled)
            db.commit()
        except Exception, e:
            notify_message("Exception in 'remove_from_already_crawled'", e, "SQL: " + sql_remove_from_already_crawled)
            db.rollback()

    def process_content(self, soup, id_of_link, content):
        print("\t\tTitle: " + soup.title.string[:50] + "...")
        list_of_meta = soup.find_all("meta")
        for meta in list_of_meta:
            if meta.has_attr('name') and str(meta['name']) == "description":
                print("\t\tDescription: " + meta['content'][:50] + "...")

            if meta.has_attr('name') and str(meta['name']) == "keywords":
                print("\t\tKeywords: " + meta['content'][:50])

        current_dir = os.getcwd()
        files_dir = current_dir + "/Originals/"
        file_name = id_of_link
        file_path = files_dir + str(file_name)
        created_file = open(file_path, "w")
        created_file.write(content.encode("utf-8"))
        created_file.close()
        print("\t\tOriginal Content Is Saved")

    def crawl(self):
        counter = 1
        db = MySQLdb.connect("localhost", "root", "", "varys", unix_socket="/opt/lampp/var/mysql/mysql.sock")
        cursor = db.cursor()

        headers = {'User-Agent': "Aditya's Browser"}

        if self.check_if_url_already_queued_or_crawled(cursor, self.base_url) == -1:
            self.insert_into_pending_urls_list(db, cursor, self.base_url)
        crawling_url, id_of_url = self.get_front_url_from_pending_urls_list(db, cursor)
        while crawling_url is not None:
            print("\t" + str(counter) + ". Crawling:  " + str(crawling_url)[:50] + "...")
            response = requests.get(crawling_url, headers=headers, verify=False)
            response_type = str(response.headers.get('content-type')).split(";")[0]
            if response_type == "application/atom+xml":
                print("\t\tCannot Crawl An XML Page!")
                self.remove_from_already_crawled(db, cursor, id_of_url)
            else:
                soup = BeautifulSoup(response.text, 'html.parser')

                self.process_content(soup, id_of_url, response.text)
                print("\t\tProcessed '" + crawling_url[:50] + "...'")

                new_links = [link["href"] for link in soup.findAll("a", href=True)]
                new_links = self.strip_links(crawling_url, new_links, remove_external=True)

                for each_link in new_links:
                    existing_id = self.check_if_url_already_queued_or_crawled(cursor, each_link)
                    if existing_id == -1:
                        row_id = self.insert_into_pending_urls_list(db, cursor, each_link)
                        self.insert_into_reference(db, cursor, id_of_url, row_id)
                        print("\t\t\tNew Url Inserted '" + each_link[:50] + "...'")
                    else:
                        self.insert_into_reference(db, cursor, id_of_url, existing_id)
                        # print("\t\tAlready Exists in Queue")

            crawling_url, id_of_url = self.get_front_url_from_pending_urls_list(db, cursor)
            counter += 1
            print("")
