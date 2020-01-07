import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nlpnews import article, newsloader

def all_citation_sents():
    """
    Get all sentiment scores for citations in all corpus as list.
    Write results to csv file.
    Return: a list of tuples: sentiment score, article source
    """

    articles = article.load_articles()
    
    sentlist = []
    for art in articles:
        for sent in art.citations_sentiment_list():
            sentlist.append((round(sent*100, 2), art.source))

    df = pd.DataFrame(sentlist, columns=["score", "source"])
    df.to_csv('./dataframes/citation_sents.csv')

    return sentlist


def opinion_sents():
    """
    Calculate sentiment scores for opinion articles.
    Store results in csv file.
    Return: a list of tuples: sentiment score, opinion source
    """
    sid = SentimentIntensityAnalyzer()

    sentlist = []
    for op in article.opinions():
        sentlist.append([round(sid.polarity_scores(op.fulltext)['compound'] *100, 2), op.source])

    df = pd.DataFrame(sentlist, columns=['score', 'souce'])
    df.to_csv('./dataframes/opinion_sents.csv')

    return sentlist


def sentiment_for_source(source):
    """
    Calculate average sentiment score for a source
    """
    articles = article.load_articles()
    articles = [art for art in articles if art.source == source]

    sentlist = []
    for art in articles:
        sentlist += art.citations_sentiment_list()
    
    return sum(sentlist) / len(sentlist)


def sentiment_for_all_sources():
    """
    Calculate sentiment score for all sources in corpus
    and store results in csv file
    """

    sourcesents = []
    for src in newsloader.SOURCES:
        score = sentiment_for_source(src)
        sourcesents.append([round(score*100, 2), src])
    
    df = pd.DataFrame(sourcesents, columns=["score", "source"])
    df.to_csv('./dataframes/source_sentiment.csv')

