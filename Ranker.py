import operator


class TFIDF:
    details_index = dict()

    def __init__(self, index):
        self.details_index = index

    def rankIt(self):
        for key, value in self.details_index.items():
            self.details_index[key] = len(value)

        sorted_list = sorted(self.details_index.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_list
