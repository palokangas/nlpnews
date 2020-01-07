import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from . import newsloader as nl 

class Article:
    """ Article class for convenience in processing """

    # Shortcut for creating instance attrs from mapping
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def get_citations(self):
        matcher = r"\"\S{1}.*?\""
        if self.source in ['the-new-york-times', 'fox-news']:
            matcher = r"\“\S{1}.*?\”"
        
        citations = re.findall(matcher, self.fulltext)
        return citations

    def citations_sentiment(self):
        sid = SentimentIntensityAnalyzer()
        cits = self.get_citations()
        try:
            return sum(sid.polarity_scores(cit)['compound'] for cit in cits) / len(cits)
        except ZeroDivisionError:
            return 0

    def citations_sentiment_list(self):
        sid = SentimentIntensityAnalyzer()
        cits = self.get_citations()
        sentlist = []
        for cit in cits:
            sentlist.append([sid.polarity_scores(cit)['compound'], cit])
        return sentlist


def load_articles(sources=None):
    if not sources:
        sources = nl.read_data()

    articlelist = []
    for pub in sources.keys():
        if pub == 'the-washington-post': continue # TWP provides garbled requests so no full text available
        for art in sources[pub]:
            # Convert dict sources to strings
            try:
                art['source'] = art['source']['id']
            except TypeError:
                pass
            art['fulltext'] = nl.get_content_for(art['uuid'])
            articlelist.append(Article(**art))
    
    return articlelist

def opinions(articles=None):
    """ Get opinion articles """

    if not articles:
        articles = load_articles(nl.read_data())
    
    opinion_arts = [a for a in articles if a.url.find("/opinion") is not -1]
    for op in opinion_arts:
        yield op




def for_source(source, articles=None):
    """ Get articles for a gives news source """
    
    if not articles:
        articles = load_articles(nl.read_data())
    
    source_arts = [a for a in articles if a.source == source]
    for art in source_arts:
        yield art

