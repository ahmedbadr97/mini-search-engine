import math
import os
import random

import numpy as np

from doc_data import Docdata


def generate_rand_files(numOfFiles, dataList, directory):
    for i in range(1, numOfFiles + 1):

        # file prefix ->doc+(index)
        # file=open(directory+'\\'+'Doc'+str(i)+'.txt','w')
        # file prifix (index)
        file = open(directory + '\\' + str(i) + '.txt', 'w')
        numofChars = random.randint(4, numOfFiles)
        for j in range(numofChars):
            file.write(dataList[random.randint(0, len(dataList) - 1)] + ' ')
        file.close()


def load_docs(directory):
    docs = []
    filenames = os.listdir(directory)
    # Load Documents
    for filename in filenames:
        docs.append(Docdata(directory + "\\" + filename))
    return docs


# _____calcualte initial idf without query_____
def calculate_ini_idf(docs_list):
    # creating a dict of keys the strings in the doc ant it's value object of IDF class which has docfreq and no of documents
    dic = {}
    for doc in docs_list:
        for key in doc.WordsFrequency.keys():
            try:
                # if key exits or the string exists increase its idf.docfreq by one
                dic[key].doc_freq += 1
            except:
                # create a new key with it value new object from idf class with docfreq=1 and no of dos lenghth of doc dict
                dic[key] = Idf(1, len(docs_list))
    return dic


def calculate_final_idf(ini_idf, queryfile):
    # increase thedocfreq of strings exist in the query
    for key in queryfile.WordsFrequency.keys():  #
        if (ini_idf.get(key) is not None):
            ini_idf[key].doc_freq += 1
    return ini_idf


def calculate_docs_weights(final_idf_dict: dict, doclist):
    for doc in doclist:
        for key, value in doc.WordsFrequency.items():
            tf = (value / doc.maxfreq)
            doc.weights[key] = tf * final_idf_dict.get(key).idf_value()


def calc_magnitudes(doc_list, final_idf_dict):
    for doc in doc_list:
        doc.CalulateMagnitude(final_idf_dict)


def adjacency_matrix_calc(doclist: list):
    A = np.zeros([len(doclist), len(doclist)], int)
    for doc in doclist:
        # dictionary of links in the document it's key is the number or filename or the link
        for link in doc.links.keys():
            # document name is a number from 0 to n link is the key of links dict
            A[int(doc.filename) - 1][int(link) - 1] = 1
    return A


def auth_hub_calc(adjMatrix, k):
    hub = np.ones([len(adjMatrix)])
    auth = np.ones([len(adjMatrix)])
    for i in range(k):
        auth = np.dot(adjMatrix.transpose(), hub)
        hub = np.dot(adjMatrix, auth)
        # normalization
        # first pass on the array and square it's values then add them then take squareroot
        auth_normalizaion = math.sqrt(sum(map(lambda x: math.pow(x, 2), auth.data)))
        hub_normalization = math.sqrt(sum(map(lambda x: math.pow(x, 2), hub.data)))
        for j in range(len(adjMatrix)):
            auth.data[j] = auth.data[j] / auth_normalizaion
            hub.data[j] = hub.data[j] / hub_normalization

    return auth, hub


class Idf:
    def __init__(self, doc_freq, no_of_docs):
        self.doc_freq = doc_freq
        self.no_of_docs = no_of_docs

    def idf_value(self):
        if self.doc_freq == 0 | self.no_of_docs == 0:
            return 0
        return math.log2((self.no_of_docs + 1) / self.doc_freq)
