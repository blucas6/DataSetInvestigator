from data import Data

def askforoutput():
    y = input(' Show output? (y/n): ')
    if y == 'y':
        return True
    return False

def printMain():
    print('\n\n=Data Analyzer= ')
    print('(A): Run similarity finder')
    print('(B): Create a graph based off the similarity finder')
    print('(C): Create a histogram for most frequent words')
    print('(D): Create a review cluster')
    print('(E): Create a frequency dictionary per column')
    print('(F): Create unique word dictionary')
    print('(G): Create histograms for unique words')
    print('(H): Regrade yourself')
    print('(I): Auto check a review')
    print('(J): Get output to feed to chatGPT')
    print('(K): Show figures')
    print('\n(Q): Quit')

if __name__=="__main__":
    myData = Data()
    while True:
        printMain()
        c = input('Command: ').lower()
        if c == 'q':
            exit()
        if c == 'a':
            try:
                o = float(input(' Set limit for minimum correlation: '))
                myData.RunSimilarityFinder(o)
            except Exception as e:
                print(e)
                myData.RunSimilarityFinder()
        elif c == 'b':
            myData.createGraph(myData.Catalogue)
        elif c == 'c':
            myData.createHistogramForReviewCluster()
        elif c == 'd':
            myData.CreateReviewCluster(showoutput=askforoutput())
        elif c == 'e':
            myData.CreateFrequencyDictByColumn()
        elif c == 'f':
            myData.FindWordUniqueness(showoutput=askforoutput())
        elif c == 'g':
            myData.createHistogramForUniqueWords()
        elif c == 'h':
            d = input(' Change depth? (10): ')
            try:
                d = int(d)
                myData.RegradeYourself(depth=d)
            except Exception as e:
                myData.RegradeYourself()
        elif c == 'i':
            myData.FullCheck(input('What review would you like to check: '), depth=20)
        elif c == 'j':
            try: 
                st = input(' Start: ')
                end = input(' End: ')
                if st:
                    st = int(st)
                if end:
                    end = int(end)
                if st and end:
                    myData.feedToGPT(start=st, end=end)
                elif st:
                    myData.feedToGPT(start=st)
                elif end:
                    myData.feedToGPT(end=end)
                else:
                    myData.feedToGPT()
            except Exception as e:
                print(e)
        elif c == 'k':
            myData.ShowFigures()
