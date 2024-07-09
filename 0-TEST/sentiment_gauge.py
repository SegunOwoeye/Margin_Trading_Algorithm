"""import nltk

nltk.download('vader_lexicon')"""

from nltk.sentiment.vader import SentimentIntensityAnalyzer
import string

def reading_dict():
    with open("0-TEST/dictionary.txt") as file:
        overall_list = []
        while line := file.readline():
            overall_list.append(line.rstrip())
    
    word_list = []
    for i in range(len(overall_list)):
        if overall_list[i][0] in string.ascii_letters:
            word_list.append(overall_list[i])
        else:
            pass

    print(word_list)

    # Strips the newline character
    word_list = []
    
    #for i in range(len(Lines)):
    #    print(Lines)
    '''if Lines[i] in string.ascii_letters:

            print(Lines[i])
            """if Lines[i].isalpha() == True:
                print(i)
                else:
                    pass"""
        else:
            print("no")'''


def rating_text_sentiment(text):
    text = text.lower()
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)

    return scores

text = "price is about to decrease"

#print(rating_text_sentiment(text))


reading_dict()