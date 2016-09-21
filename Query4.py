#!/usr/bin/env python
import MySQLdb
import json

from nltk.corpus import stopwords
from nltk.stem.porter import *
from CommonUtils import notify_message


class Query:

    def find_id_of_word(self, cursor, word):
        sql_select_id_of_word = """select id from indexed_words where word='""" + word + """'"""
        try:
            cursor.execute(sql_select_id_of_word)
            if cursor.rowcount > 0:
                return cursor.fetchone()[0]
            else:
                return -1
        except Exception, e:
            print(e.message)
            print("Exception in Find Id Of Word")
            notify_message("Exception in Find Id Of Word")
            return -1

    def get_file_ids_based_on_word(self, cursor, word_id, limit, offset):
        sql_select_file_ids = """select file_id, count(position) as count \
        from words_mapping \
        where word_id=""" + str(word_id) + """ \
        group by file_id \
        ORDER by COUNT desc \
        limit """ + str(limit) + """ \
        OFFSET """ + str(offset)
        try:
            cursor.execute(sql_select_file_ids)
            if cursor.rowcount > 0:
                result = cursor.fetchall()
                return result
            else:
                return None
        except Exception, e:
            print(e.message)
            print("Exception in get File Ids for Word")
            notify_message("Exception in get File Ids for Word")
            return None

    def get_meta_info_for_id(self, cursor, file_id):
        title = str()
        description = str()
        link = str()
        sql_select_meta_info = """select m.title, m.description, acl.link from meta_info_of_links as m, already_crawled_links as acl where  m.id=acl.id and m.id=""" + str(file_id)
        try:
            cursor.execute(sql_select_meta_info)
            if cursor.rowcount > 0:
                result = cursor.fetchone()
                return result[0], result[1], result[2]
            else:
                print("No such file id")
                return None, None, None
        except Exception, e:
            print(e.message)
            print("Exception in get File Ids for Word")
            notify_message("Exception in get File Ids for Word")
            return None, None, None

    def query_one_word(self, word, limit=10, offset=0):
        db = MySQLdb.connect("localhost", "root", "", "varys", unix_socket="/opt/lampp/var/mysql/mysql.sock")
        cursor = db.cursor()

        stemmer = PorterStemmer()
        stopwords_list = stopwords.words('english')

        # print("\tQuerying Word...'" + word + "'")

        if word in stopwords_list:
            print("\t\tNot enough for searching...")
        else:
            stemmed_word = str(re.sub(r'\W+', '', stemmer.stem(word)))
            word_id = self.find_id_of_word(cursor, stemmed_word)
            if word_id == -1:
                print("\t\tNot such word found...")
            else:
                result = self.get_file_ids_based_on_word(cursor, word_id, limit, offset)
                json_array_result = list()
                for row in result:
                    json_object = dict()
                    title, description, link = self.get_meta_info_for_id(cursor, row[0])
                    json_object["title"] = title
                    json_object["description"] = description
                    json_object["link"] = link
                    json_array_result.append(json_object)
                print(json.dumps(json_array_result))

