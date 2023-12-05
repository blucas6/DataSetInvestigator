import pandas as pd
import os
import string
import re
import networkx as nx

from graph import Figures
from frequency import FrequencyDict

class Data:
    def __init__(self):
        self.files = []
        self.rawdata = pd.DataFrame()
        self.DATADIR = "data"
        self.ANSWERDIR = "answer"

        self.DataFigures = Figures()

        self.FilteredWords = ['the', 'to', 'for', 'a', 'and', 'in', 'is', 'of', 'with', 'that', 'from', 'this', 'be', 'not', 'it', 'on', 'changeid', 'security']

        # Holds a frequency dict for each column
        self.FrequencyDict = {}     # { 'columnname': FrequencyDict, 'columnname': FrequencyDict }

        # Holds a frequency dict for each review
        self.ReviewCluster = {}     # Groups most frequent words by review

        self.answersdata = pd.DataFrame()

        # holds a each review as a dictionary holding each other reviews correlation to itself
        self.Catalogue = {}         # { 'reviewname': {'reviewname': correlation, 'reviewname': correlation } }
        self.FreqCatalogue = {}     # { 'reviewname': FrequencyDict }

        self.FIGURES = 1

        # dictionary of all words in training data - record of which type of reviews they appear in
        self.WordDict = {}          # { word: [review_type, review_type, ...] }

        # dictionary of all review types and their most unique words
        self.ReviewUniqueness = {}  # { review_type: [[word, #], [word, #], [word, #], ...] }

        self.ReadinData()

    def cleanWord(self, word):
        word = word.lower()
        translator = str.maketrans('', '', string.punctuation)
        word = word.translate(translator)
        if bool(re.search(r'\d', word)):
            return ''
        if word in self.FilteredWords:
            return ''
        if word.isdigit():
            return ''
        else:
            return word

    def FindWordUniqueness(self, showoutput=False, depthofprint=10):
        if self.answersdata.empty:
            print('Error: No answers data is loaded!')
            return
        # go through answer data
        for index, row in self.answersdata.iterrows():
            # go through description for row word by word
            for word in str(row['description']).split():
                # clean word
                word = self.cleanWord(word)
                if word:
                    # if word is already in word dict
                    if word in self.WordDict:
                        # but type of answer is not already in the list of associated answers to that word add it to the list
                        if not row['answer'] in self.WordDict[word]:
                            self.WordDict[word].append(row['answer'])
                    else:
                        # otherwise add an index for that word and that answer type
                        self.WordDict[word] = [row['answer']]
        if showoutput:
            print("\n=Most Unique Words=")
            for word in self.WordDict.keys():
                if len(self.WordDict[word]) == 1:
                    print(f'Word: "{word}"\t\t\tReview: {self.WordDict[word]}')
        # go through answers again
        for index, row in self.answersdata.iterrows():
            # go through description for row word by word
            for word in str(row['description']).split():
                # clean word
                word = self.cleanWord(word)
                # check if word is in the worddict and it is unique to one type of review
                if word and word in self.WordDict and len(self.WordDict[word]) == 1:
                    reviewtype = self.WordDict[word][0]
                    # check if that review is in the dict
                    if reviewtype in self.ReviewUniqueness:
                    # if it is check if it already has that word
                        if word in self.ReviewUniqueness[reviewtype]:
                            self.ReviewUniqueness[reviewtype][word] += 1
                        else:
                            self.ReviewUniqueness[reviewtype][word] = 1
                    else:
                        # add review type to dict and give it a dict of words
                        self.ReviewUniqueness[reviewtype] = {word: 1}
        # sort all the dicts
        for key in self.ReviewUniqueness.keys():
            self.ReviewUniqueness[key] = {k: v for k,v in sorted(self.ReviewUniqueness[key].items(), key=lambda x: x[1])}
        if showoutput:
            print('\n=Unique Words per Review Type=')
            for review in self.ReviewUniqueness.keys():
                tmp = {}
                words = list(self.ReviewUniqueness[review].keys())
                if len(words)-1-depthofprint < 0:
                    min = 0
                else:
                    min = len(words)-1-depthofprint
                if words:
                    for word in range(len(words)-1, min, -1):
                        tmp[words[word]] = self.ReviewUniqueness[review][words[word]]
                print(f'Review type: {review}\t\t\t{tmp}')

    def RegradeYourself(self, depth=10):
        if self.answersdata.empty:
            print('Error: No answers data is loaded!')
            return
        total = len(self.answersdata)
        count = 0
        score = {}
        for index, row in self.answersdata.iterrows():
            answer,perc = self.AutoCheckReview(row['description'], depth=depth)
            if answer == '' or perc == -1:
                print("Auto check failed!")
                return
            if answer == row['answer']:
                count += 1
                if answer in score:
                    score[answer][0] += 1
                    score[answer][1] += 1
                else:
                    score[answer] = [1, 1, 0]
            else:
                if row['answer'] in score:
                    score[answer][1] += 1
                    score[answer][2] += 1
                else:
                    score[answer] = [0, 1, 1]
        print()
        for key in score.keys():
            if len(key) > 24:
                tab = '\t'
            elif len(key) > 23:
                tab = '\t\t'
            elif len(key) < 15:
                tab = '\t\t\t\t'
            else:
                tab = '\t\t\t'
            print(f'{key}{tab}[{score[key][0]}/{score[key][1]}] {round(100*(score[key][0]/score[key][1]), 2)}%\tMisses [{score[key][2]}/{score[key][1]}] {round(100*(score[key][2]/score[key][1]), 2)}%')
        
        print(f'\nRegrade Score: {count}/{total} - {round(100*(count/total),2)}%\n')

    def FullCheck(self, description, depth=10):
        if self.ReviewUniqueness:
            if self.ReviewCluster:
                answer, perc = self.AutoCheckReview(description, depth=depth)
                print('\n=Unique Word Check=')
                for word in str(description).split():
                    for review in self.ReviewUniqueness.keys():
                        if word in self.ReviewUniqueness[review]:
                            print(f'Unique word hit "{word}" -> {review}')
                print(f'\nClosest Match >>> {answer} {perc}%\n')
            else:
                print('Error: Build Review Cluster first!')
        else:
            print('Error: Build Unique Review Dictionary first!')

    def AutoCheckReview(self, description, depth=10):
        if self.ReviewCluster:
            review = FrequencyDict(description, 'sample')
            print(f'\n=SAMPLE=\n{review.data}\n========\n')
            min = 0
            answer = ''
            print('=Stats=')
            for key in self.ReviewCluster.keys():
                perc = review.CompareFrequencies(self.ReviewCluster[key], depth=depth)
                if perc > min:
                    min = perc
                    answer = key
                print(f'{key} - {round(perc,2)}')
            if not answer:
                answer = next(iter(self.ReviewCluster))
            return answer,round(min*100,2)
        else:
            print('Error: Build review cluster first!')
            return '', -1

    def feedToGPT(self, start=0, end=-1):
        if not self.rawdata.empty:
            print("===GPT OUTPUT===\n")
            rowc = 2
            endc = end
            for index, row in self.rawdata.iterrows():
                if rowc > endc and endc != -1:
                    break
                if rowc >= start:
                    print(f"URL: '{row['url']}', Description: '{row['description']}',")
                rowc += 1
            print("\n===GPT OUTPUT===")
        else:
            print('Error: no data is loaded!')

    def createGraph(self, mydict):
        if mydict:
            self.DataFigures.createGraph(mydict)
            print('Graph done!')
        else:
            print('Error: Run similarity finder first!')
        
    def dumpColumn(self, columnname):
        print(self.rawdata[columnname].tolist())

    def cleanWord(self, word):
        word = word.lower()
        translator = str.maketrans('', '', string.punctuation)
        word = word.translate(translator)
        if bool(re.search(r'\d', word)):
            return ''
        if word in self.FilteredWords:
            return ''
        if word.isdigit():
            return ''
        else:
            return word
        
    def sortDict(self, d):
        return {k: v for k,v in sorted(d.items(), key=lambda x: x[1])}
    
    def RunSimilarityFinder(self, min_correlation=0.8):
        if not self.rawdata.empty:
            # create frequencydicts for all reviews first
            for index, row in self.rawdata.iterrows():
                self.FreqCatalogue[row['url']] = FrequencyDict(row['description'], name=row['url'])
            # process data row by row
            for index, row in self.rawdata.iterrows():
                # create tmp dict to hold all the comparison data
                compare = {}
                # loop through freqcatalogue to compare with fd
                for review in self.FreqCatalogue.keys():
                    # check if review is not the one currently processing
                    if not review == row['url']:
                        # find similarity percentage
                        percent = self.FreqCatalogue[row['url']].CompareFrequencies(self.FreqCatalogue[review])
                        # if close enough, add to dictionary of close reviews
                        if percent > min_correlation:
                            compare[review] = percent
                # add similarity dict to catalogue
                self.Catalogue[row['url']] = compare
            print('Similarity finder done!')
        else:
            print('Error: No data is loaded!')
    
    def BuildCluster(self):
        if self.Catalogue:
            bucket = 0
            Catalogue = self.Catalogue
            # Find all reviews with high correlations
            while True:
                most = 0
                saver = ""
                for review in Catalogue.keys():
                    # go through that reviews correlations
                    corrs = len(Catalogue[review].keys())
                    if corrs > most:
                        saver = review
                if saver:
                    # current highest correlations
                    # add to bucket
                    self.Catalogue[bucket] = [saver]
                    del Catalogue[saver] 
        else:
            print('Error: Run Similarity Finder first!')

    def CreateReviewCluster(self, columnname='description', showoutput=False):
        if self.answersdata.empty:
            print('Error: No answers data is loaded!')
            return
        # loop through answer data
        for index, row in self.answersdata.iterrows():
            # check if answer is already in the reviewcluster
            if not row['answer'] in self.ReviewCluster:
                # if not already in review cluster, create frequency dict for that answer row
                self.ReviewCluster[row['answer']] = FrequencyDict(row[columnname], row['answer']+' - 0')
            else:
                # else take the row data and add it to the current reviewcluster data and create a new freqdict
                data = row[columnname] + self.ReviewCluster[row['answer']].data
                self.ReviewCluster[row['answer']] = FrequencyDict(data, row['answer'])
        if showoutput:
            for key in self.ReviewCluster.keys():
                mask = self.answersdata['answer'] == key
                print(f'{key} - {mask.sum()}')
                print(self.ReviewCluster[key].printDict(10))
        print('Review cluster created!')

    def CreateFrequencyDictByColumn(self):
        if not self.rawdata.empty:
            for col in self.rawdata.columns:
                data = ""
                for strg in self.rawdata[col].tolist():
                    data += str(strg)+" "
                fd = FrequencyDict(data, col)
                if not col in self.FrequencyDict:
                    self.FrequencyDict[col] = fd
            print('FREQUENCIES BY COLUMN')
            for key in self.FrequencyDict.keys():
                self.FrequencyDict[key].printDict(10)
        else:
            print('Error: No data is loaded!')

    def ReadinData(self):
        self.files = os.listdir(self.DATADIR)
        for f in self.files:
            f = os.path.join(self.DATADIR, f)
            if os.path.isfile(f):
                dft = pd.read_csv(f, encoding='utf-8')
                self.rawdata = pd.concat([self.rawdata, dft])
            else:
                print(f'File not found: {f}')
        self.files = os.listdir(self.ANSWERDIR)
        tmpframe = pd.DataFrame()
        for f in self.files:
            f = os.path.join(self.ANSWERDIR, f)
            if os.path.isfile(f):
                dft = pd.read_csv(f, encoding='utf-8')
                tmpframe = pd.concat([self.answersdata, dft])
        self.answersdata = tmpframe.dropna(subset=[tmpframe.columns[-1]])
        print("DATA LOADED...\n")

    def getTopValuesFromDict(self, thedict, top=10):
        tmp = {}
        words = list(thedict.keys())
        if words:
            for word in range(len(words)-1, len(words)-1-top, -1):
                tmp[words[word]] = thedict[words[word]]
        return tmp
    
    def createHistogramForUniqueWords(self):
        if self.ReviewUniqueness:
            for review in self.ReviewUniqueness.keys():
                self.createHistogram(self.ReviewUniqueness[review], name=review)
            print('Histogram created!')
        else:
            print('Error: Create Unique Review Dict first!')

    def createHistogramForReviewCluster(self):
        if self.ReviewCluster:
            for review in self.ReviewCluster.keys():
                self.createHistogram(self.ReviewCluster[review].rawdict, review)
            print('Histogram created!')
        else:
            print('Error: Create a review cluster first!')

    def createHistogram(self, mydict, name='sample'):
        if mydict:
            self.DataFigures.createHistogram(mydict, name)
        else:
            print('Error: Provided dictionary to histogram is empty!')

    def ShowFigures(self):
        self.DataFigures.showFigures()