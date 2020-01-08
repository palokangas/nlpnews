from collections import defaultdict
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from nlpnews import article, analysis

def get_comparison_topics(nr_topics=3):
    opinions = list(article.opinions())
    news = [a for a in article.load_articles() if a.uuid not in [op.uuid for op in opinions]]

    newstopics = get_topics(news)
    opiniontopics = get_topics(opinions)
    pd.DataFrame(newstopics).to_csv('./dataframes/newstopics.csv')
    pd.DataFrame(opiniontopics).to_csv('./dataframes/opiniontopics.csv')
    
    shared_tokens = []
    jaccard_table = []
    for ntopic in newstopics:
        row = []
        for optopic in opiniontopics:
            word_in_both = set(w for w in ntopic if w in optopic)
            nr_all = len(ntopic)
            nr_both = len(word_in_both)
            jaccard = nr_both / nr_all
            row.append(jaccard)
            if jaccard > 0:
                shared_tokens += [a for a in ntopic if a in optopic]

        jaccard_table.append(row)

    df = pd.DataFrame(jaccard_table)
    df.to_csv('./dataframes/lda.csv')

    worddict = defaultdict(int)
    for w in shared_tokens:
        worddict[w] += 1

    worddict = {k:v for k,v in sorted(worddict.items(), key=lambda x: -x[1])}
    df2 = pd.DataFrame(list(zip(worddict.keys(), worddict.values())), columns = ["token", "count"])
    df2.to_csv('./dataframes/lda_most_common.csv')

    print("Shared tokens:")
    print(worddict)
    return jaccard_table


def get_topics(articles, nr_topics=3):
    """
    Use LDA to extract nr_topics number of topics.
    """

    # Make articles into a simple list
    artlist = []
    publist = []

    for art in articles:
        artlist.append(art.fulltext)
        publist.append(art.source)

    data = {'article': artlist, 'publication': publist}
    artdata = pd.DataFrame(data)

    cv = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    dtm = cv.fit_transform(artdata['article'])

    LDA = LatentDirichletAllocation(n_components=nr_topics, random_state=42)
    LDA.fit(dtm)

    topiclist = []
    topicdict = {}
    for index, topic in enumerate(LDA.components_):
        top = [cv.get_feature_names()[i] for i in topic.argsort()[-5:]]
        print(top)
        topiclist.append(top)
        #topicdict[index] = [cv.get_feature_names()[i] for i in topic.argsort()[-5:]]
        
    return topiclist

