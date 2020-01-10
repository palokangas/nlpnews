# Plotting workflow based on tips from https://blog.heptanalytics.com/flask-plotly-dashboard/
# And: https://code.tutsplus.com/tutorials/charting-using-plotly-in-python--cms-30286

import string
import re
import json
from collections import defaultdict

import plotly 
import plotly.graph_objs as go
import pandas as pd 
import numpy as np 
import nltk
from nltk import word_tokenize, FreqDist, bigrams, trigrams
from nltk.corpus import stopwords
from . import article, newsloader

# Load english stopwords
stopwords = nltk.corpus.stopwords.words('english')

# Additional words for removal
WORDS_FOR_REMOVAL = "'s said greta thunberg climate change n't would like ms".split()

# Add more punctuation to defaults
additionalpunct = "“’”—"
punct = list(string.punctuation + additionalpunct)

def extra_tokenize(srctext):
    """
    Use nltk's word_tokenize first
    and then also check if the remaining tokens are all punctuation
    and if so, remove those tokens
    """
    alltokens = word_tokenize(srctext)
    newtokens = []
    for token in alltokens:
        allpunct = False
        if token[0] in punct:
            allpunct = True
            for w in list(token):
                if w in punct:
                    pass
                else:
                    allpunct = False
        if not allpunct:
            newtokens.append(token)
    return newtokens


def get_most_common_terms(articles=None):
    """ Return most common terms in all texts, or in selected articles if given """

    if not articles:
        articles = article.load_articles()

    alltext = "\n".join(art.fulltext for art in articles)
    alltokens = extra_tokenize(alltext)

    all_to_remove = stopwords + punct + WORDS_FOR_REMOVAL
    coretokens = [t.lower() for t in alltokens if t.lower() not in all_to_remove]
    fd = FreqDist(coretokens)

    df = pd.DataFrame(fd.most_common(20), columns=["word", "freq"])
    df.to_csv('./dataframes/most_common.csv')
    return fd.most_common(20)


def get_jaccard_for(text1, text2):
    """ Calculate a jaccard score of two texts """
    
    ##    
    #        tokens = analysis.extra_tokenize(self.fulltext)
    #    all_to_remove = stopwords + punct + WORDS_FOR_REMOVAL
    #    coretokens = [t.lower() for t in tokens if t.lower() not in all_to_remove]
    #    fd = FreqDist(coretokens)
    
    #tokens1 = word_tokenize(text1)
    #tokens2 = word_tokenize(text2)
    #all_to_remove = WORDS_FOR_REMOVAL + stopwords + punct
    #tokens1 = [t.lower() for t in tokens1 if t.lower() not in all_to_remove]
    #tokens2 = [t.lower() for t in tokens2 if t.lower() not in all_to_remove]
    #fdist1 = FreqDist(tokens1)
    #fdist2 = FreqDist(tokens2)
    #print(fdist1.most_common(20))
    #print(fdist2.most_common(20))
    #wordlist1 = list(fdist1.most_common(20))
    #wordlist2 = list(fdist2.most_common(20))
    wordlist1 = [w[0] for w in text1.common_terms()]
    wordlist2 = [w[0] for w in text2.common_terms()]
    print(wordlist1)
    
    all_popular_words = set(wordlist1 + wordlist2)
    word_in_both = set(w for w in wordlist1 if w in wordlist2)
    nr_all = len(all_popular_words)
    nr_both = len(word_in_both)
    jaccard = nr_both / nr_all
    common_words = ", ".join(word_in_both)
    print("Words in both texts: ", common_words)
    print(f"Jaccard = {nr_both} / {nr_all} = {jaccard:.3f}")
    return jaccard


def comparison_table():
    """
    Create a table with Jaccard index of articles vs. opinion articles
    Store in CSV and return as a table
    """
    opinions = list(article.opinions())
    #news = [a for a in article.load_articles() if a.uuid not in [op.uuid for op in opinions]]
    news = article.news_articles()

    shared_tokens = []
    datatable = []
    columns = [str(i)+'-'+op.source for i, op in enumerate(opinions)]
    for art in news:
        row = []
        for op in opinions:
            jac = round(get_jaccard_for(art, op) *100, 2)
            row.append(jac)
            # If there is even small similarity, collect similar tokens
            if jac > 0:
                acom = [w[0] for w in art.common_terms()]
                opcom = [w[0] for w in art.common_terms()]
                shared_tokens += [artword for artword in acom if artword in opcom]

        datatable.append(row)

    df = pd.DataFrame(datatable, columns=columns)
    df.to_csv('./dataframes/jaccard.csv')

    worddict = defaultdict(int)
    for w in shared_tokens:
        worddict[w] += 1
    worddict = {k:v for k,v in sorted(worddict.items(), key=lambda x: -x[1])}
    
    df2 = pd.DataFrame(list(zip(worddict.keys(), worddict.values())), columns = ["token", "count"])
    df2.to_csv('./dataframes/jaccard_most_common.csv')

    return worddict


def plot_freqs():

    df = pd.read_csv('./dataframes/most_common.csv')
    data = [
        go.Bar(
            y=df['freq'],
            x=df['word'],
            orientation='v',
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def plot_jaccard():

    df = pd.read_csv('./dataframes/jaccard.csv')
    data = [
        go.Scatter(
            x=df.columns[1:],
            y=df.index,
            mode='markers',
            
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def plot_sentimentbar():

    df = pd.read_csv('./dataframes/sents_sources.csv')
    data = [
        go.Bar(
            x=df['source'],
            y=df['score']
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

## This is here just for reference on how to manipulate colors :-)
def plot_sentimentscatter():

    df = pd.read_csv('./dataframes/sents_citations.csv')

    # Create colors for markers
    colorsIdx = {'bbc-news': 'rgb(215,40,39)',
                 'abc-news-au': 'rgb(215,80,39)',
                 'the-new-york-times': 'rgb(215,120,39)',
                 'fox-news': 'rgb(215,160,39)',
                 'al-jazeera-english': 'rgb(215,200,39)',
                }
    cols      = df['source'].map(colorsIdx)

    data = [
        go.Scatter(
            x=df.index,
            y=df['score'],
            mode='markers',
            marker=dict(color=cols),            
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def plot_entitybars():

    df = pd.read_csv('./dataframes/entities.csv')
    data = [
        go.Bar(
            y=list(reversed(df['token'])),
            x=list(reversed(df['count'])),
            orientation='h',
        )
    ]


    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
    

def plot_sentimentscatter2():

    df = pd.read_csv('./dataframes/sents_citations.csv')

    data = []

    for src in newsloader.SOURCES:
        dfs = df[df['source'] == src]
        src_data = [
            go.Scatter(
                x=dfs.index,
                y=dfs['score'],
                mode='markers',
                marker=dict(size=16),
                hovertext=dfs['citation'],
                name=src,   
            )
        ]
        data += src_data

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def plot_opinionscatter():

    df = pd.read_csv('./dataframes/sents_opinion.csv')

    data = []
    for src in newsloader.SOURCES:
        dfs = df[df['source'] == src]
        if len(dfs) == 0: continue
        src_data = [
            go.Scatter(
                x=dfs.index,
                y=dfs['score'],
                mode='markers',
                marker=dict(size=16),
                hovertext=dfs['title'],
                name=src,
            )
        ]
        data += src_data
    
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def plot_articlescatter():

    df = pd.read_csv('./dataframes/sents_articles.csv')

    data = []
    for src in newsloader.SOURCES:
        dfs = df[df['source'] == src]
        if len(dfs) == 0: continue 
        src_data = [
            go.Scatter(
                x=dfs.index,
                y=dfs['score'],
                mode='markers',
                marker=dict(size=16),
                hovertext=dfs['title'],
                name=src
            )
        ]
        data += src_data

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def plot_popinionscatter():

    df = pd.read_csv('./dataframes/sents_opinion_paragraphs.csv')

    data = []
    for src in newsloader.SOURCES:
        dfs = df[df['source'] == src]
        if len(dfs) == 0: continue
        src_data = [
            go.Scatter(
                x=dfs.index,
                y=dfs['score'],
                mode='markers',
                marker=dict(size=16),
                hovertext=dfs['paragraph'],
                name=src,
            )
        ]
        data += src_data
    
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON