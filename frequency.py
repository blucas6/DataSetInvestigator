import string
import re

class FrequencyDict:
    # Dictionary of all words in a review and their respective frequencies - without the filtered words list
    def __init__(self, data, name=''):
        self.name = name
        self.data = data
        self.rawdict = {}
        self.FilteredWords = ['the', 'to', 'for', 'a', 'and', 'in', 'is', 'of', 'with', 'that', 'from', 'this', 'be', 'not', 'it', 'on', 'changeid', 'we', 'as', 'signedoffby', 'by', 'will', 'use', 'when', 'if', 'an', 'are']
        self.BuildFrequencyDict()

    def CompareFrequencies(self, otherFD, depth=10):
        total = len(self.rawdict.keys())
        # as long as depth is still smaller than the total length, otherwise keep total the actual length of the dict
        if total > depth:
            total = depth
        count = 0
        depthc = 0
        # go through keys
        for key in self.rawdict.keys():
            depthc += 1
            # check if done depthwise
            if depthc > total:
                break
            # go through other dict for matches
            if key in otherFD.rawdict:
                count += 1

        return count/total

    def printDict(self, top=-1):
        if top == -1:
            top = len(self.rawdict.keys())-1
        tmp = self.getTopValuesFromDict(top)
        print(f'=FrequencyDict [{self.name}]=')
        for key in tmp.keys():
            print(f"  '{key}': {tmp[key]}")

    def getTopValuesFromDict(self, top=10):
        tmp = {}
        words = list(self.rawdict.keys())
        if len(words)-1-top < 0:
            min = 0
        else:
            min = len(words)-1-top
        if words:
            for word in range(len(words)-1, min, -1):
                tmp[words[word]] = self.rawdict[words[word]]
        return tmp

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
        
    def BuildFrequencyDict(self):
        for word in str(self.data).split():
            word = self.cleanWord(word)
            if word:
                if word in self.rawdict:
                    self.rawdict[word] += 1
                else:
                    self.rawdict[word] = 1
        self.rawdict = self.sortDict(self.rawdict)

