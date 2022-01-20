import pygal
from flask import Flask, render_template, request

import results
from doc_data import Docdata

app = Flask(__name__)
from globals import *


def load_data():
    global docs, adjacency_matrix, ini_idf, hub, auth
    docs = results.load_docs(data_directory)
    ini_idf = results.calculate_ini_idf(docs)
    adjacency_matrix = results.adjacency_matrix_calc(docs)
    auth, hub = results.auth_hub_calc(adjacency_matrix,20)  # returns auth and hub vectors takes the adj matrix and number or iter
    print(auth)
    print(hub)
    print(adjacency_matrix)


@app.route('/')
def home():
    return render_template('Query.html', submit=0)


# Generate Function
@app.route('/gen', methods=['GET', 'POST'])
def gen():
    nooffiles = int(request.form['noOfFiles'])
    # adding random numbers of file names in the random list
    filenumberslist = [str(i) for i in range(1, nooffiles + 1)]
    results.generate_rand_files(nooffiles, ['A', 'B', 'C', 'D', 'E'] + filenumberslist, data_directory)
    return render_template('Query.html')


@app.route('/query', methods=['GET', 'POST'])
def query():
    load_data()
    if request.method == 'POST':
        q = request.form['q']
        # create query file
        temp = open('Query.txt', 'w')
        temp.write(q)
        temp.close()
        # loadQueryfile
        queryfile = Docdata('Query.txt')
        # Calulate FinalIDF after getting the query c
        Final_idf = results.calculate_final_idf(ini_idf, queryfile)
        # Caculate the documents weights and save them in doc.weights dict
        results.calculate_docs_weights(Final_idf, docs)
        # Caculate the documents magnetide and save them in doc.weights dict
        results.calc_magnitudes(docs, Final_idf)
        # calculate Query Weights
        for key, value in queryfile.WordsFrequency.items():
            tf = (value / queryfile.maxfreq)
            if (Final_idf.get(
                    key) is None):  # yb2a al klma deh mesh mwgoda f al docs asln yb2a al idf bt3ha (n+1/1)=n+1 w al tf
                queryfile.weights[key] = tf * (len(docs) + 1)
            else:
                # finalidf is a dict of idf class which has two attr denminator for idf which is docsfreq of the char and numerator no of docs
                # key is the char or string get it's value from idf dict
                queryfile.weights[key] = tf * Final_idf.get(key).idf_value()
        # caculate Query Magnitude
        queryfile.CalulateMagnitude(Final_idf)
        # result is a dict with key filename and vaule cousin sim(weights)
        result = {}

        for doc in docs:
            result[doc.filename] = 0
            # calculate every string in query with Strings in doc weights
            for key, weight in queryfile.weights.items():
                # dot product every query weight of string * the weight of the same str in the doc
                if (doc.weights.get(key) is not None):
                    result[doc.filename] += (weight * doc.weights[key])
            try:
                # divide result by the mag if it is not zero
                result[doc.filename] = result[doc.filename] / (queryfile.magnitude * doc.magnitude)
            except:
                result[doc.filename] = 0
        # flag for checking no match found
        Match = True
        # sort results and popout zero Results
        FilterdResults = ResultFilter(result)
        if (len(FilterdResults) == 0):
            Match = False
        # Filterd and Sorted Auth (QueryFilteredResult,Auth,Hub)

        auth_hub_ResultDict = auth_hubFilter(FilterdResults, auth, hub)
        graph_data = graph(auth_hub_ResultDict)
        return render_template('Result.html', Match=Match, result=FilterdResults, graph_data=graph_data,
                               auth_hub_ResultDict=auth_hub_ResultDict)


@app.route('/<filename>')
def openfiles(filename):
    try:
        file = open(data_directory + '\\' + filename + ".txt")
        data = file.read()
        file.close()
        return data
    except:
        return "File Not Found"


def ResultFilter(Result):  # sorting and removing docs with 0 values
    max = 0
    FilterdResults = {}
    while len(Result) > 0:
        max = next(iter(Result.values()))
        maxkey = next(iter(Result.keys()))
        for key, value in Result.items():
            if (value > max):
                max = value
                maxkey = key
        FilterdResults[maxkey] = round(max, 3)
        if (FilterdResults[maxkey] == 0):
            FilterdResults.pop(maxkey)
        Result.pop(maxkey)
    return FilterdResults


def graph(auth_hubDict):
    line_chart = pygal.Bar()
    line_chart.title = 'Authority and Hub Graph'
    line_chart.x_labels = map(lambda s: 'Doc' + str(s), iter(i for i in auth_hubDict.keys()))
    line_chart.add('Authority', list(i[0] for i in auth_hubDict.values()))
    line_chart.add('Hub', list((i[1]) for i in auth_hubDict.values()))
    graph_data = line_chart.render_data_uri()
    return graph_data


def auth_hubFilter(QueryResults: dict, auth, hub):
    docnumbers = [int(key) for key in QueryResults.keys()]
    Result_Dict = {}
    for i in docnumbers:
        # dic the key is the filename from returned results which is numbers and values is list [it's auth,it's hub]
        Result_Dict[i] = [auth[i - 1], hub[i - 1]]  # doc1 index in hub and auth is 0
    FilterdResults = {}
    while len(Result_Dict) > 0:
        max = (next(iter(Result_Dict.values())))[0]
        maxkey = next(iter(Result_Dict.keys()))
        for key, value in Result_Dict.items():
            if (value[0] > max):
                max = value[0]
                maxkey = key
        authvalue = round(((Result_Dict[maxkey])[0]), 3)
        hubvalue = round(((Result_Dict[maxkey])[1]), 3)
        FilterdResults[maxkey] = [authvalue, hubvalue]
        Result_Dict.pop(maxkey)
    return FilterdResults


if __name__ == '__main__':
    app.run(debug=True)
