import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import pos_tag
from afinn import Afinn
from nlpnews import article, newsloader


def article_citation_sents():
    """
    Calculate sentiment scores for individual articles.
    Write results to csv file
    Return: a list of tuples: sentiment score, article source
    """

    articles = article.news_articles()

    sentlist = []
    for art in articles:
        sentlist.append((round(art.citations_sentiment(), 2), art.source, art.title))

    df = pd.DataFrame(sentlist, columns=['score', 'source', 'title'])
    df.to_csv('./dataframes/sents_articles.csv')

    return sentlist


def all_citation_sents():
    """
    Get all sentiment scores for citations in all corpus as list.
    Write results to csv file.
    Return: a list of tuples: sentiment score, article source
    """

    articles = article.news_articles()
    
    sentlist = []
    for art in articles:
        for sent, citation in art.citations_sentiment_list():
            sentlist.append((round(sent*100, 2), art.source, citation))

    df = pd.DataFrame(sentlist, columns=["score", "source", "citation"])
    df.to_csv('./dataframes/sents_citations.csv')

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
        sentlist.append([round(sid.polarity_scores(op.fulltext)['compound'] *100, 2), op.source, op.title])

    df = pd.DataFrame(sentlist, columns=['score', 'source', 'title'])
    df.to_csv('./dataframes/sents_opinion.csv')

    return sentlist


def opinion_paragraph_sents():
    """
    Calculate sentiment scores for opinion articles per paragraph.
    Store results in csv file.
    Return: a list of tuples: sentiment score, opinion source
    """
    sid = SentimentIntensityAnalyzer()

    sentlist = []
    for op in article.opinions():
        for paragraph in op.fulltext.splitlines():
            sentlist.append([round(sid.polarity_scores(paragraph)['compound'] *100, 2), op.source, paragraph])

    df = pd.DataFrame(sentlist, columns=['score', 'source', 'paragraph'])
    df.to_csv('./dataframes/sents_opinion_paragraphs.csv')

    return sentlist


def sentiment_for_source(source):
    """
    Calculate average sentiment score for a source
    """
    articles = article.load_articles()
    articles = [art for art in articles if art.source == source]

    sentlist = []
    for art in articles:
        sentlist += [value for value, _ in art.citations_sentiment_list()]
    
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
    df.to_csv('./dataframes/sents_sources.csv')

