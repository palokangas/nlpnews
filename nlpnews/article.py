from . import newsloader as nl 

class Article:
    """ Article class for convenience in processing """

    # Shortcut for creating instance attrs from mapping
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def load_articles(sources):
    articlelist = []
    for pub in sources.keys():
        for art in sources[pub]:
            #print(type(art))
            #print(art['source'])
            # Only source value is NOT a string so make that into one also
            #art['source'] = art['source']['id']
            art['fulltext'] = nl.get_content_for(art['uuid'])
            articlelist.append(Article(**art))
    
    return articlelist
