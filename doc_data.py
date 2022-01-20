import math
class Docdata:
#___________Constructor____________
    def __init__(self,filePath) :
        self.magnitude=0
        self.WordsFrequency = {}
        # (tf*IDF) DICT for Index are strings of the documents
        self.weights={}
        self.links={}# key=thedoclink value occurrence freq
        #________________file reading acording to sent path______________________
        #take the last string in the path \a\b\file.txt split on \ and take the last index then split with dot and take the first index
        self.filename=((filePath.split('\\'))[-1]).split('.')[0]
        self.file=open(filePath)
        self.filedata=self.file.read()
        words=self.filedata.split()
        self.freqSum = len(words)
        #calculate words Frequencey Dict
        for word in words :
            try:
                # take only Strings
                if word.isalpha():
                    self.WordsFrequency[word]+=1
                else:#for numbers or links
                    if(word!=self.filename):
                        try:
                            #link already in the doc so ++
                            self.links[word]+=1
                        except:
                            #it is the first occurence then add the key with value 1
                            self.links[word]=1


            except:
                self.WordsFrequency[word]=1
        self.file.close()
        #_________________________________________________________________________
        if(self.WordsFrequency.__sizeof__()>0):
            self.maxfreq=max(self.WordsFrequency.values())
#__________________________________________
    def CalulateMagnitude(self,idf):
        if(self.weights.__len__()!=0):
            for key,value in self.weights.items():
                #calculating magnitude sum of weights(i) squared
                self.magnitude+=math.pow(value,2)
            #taking Squareroot
            self.magnitude=math.sqrt(self.magnitude)







