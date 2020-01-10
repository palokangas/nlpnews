import sys
import os
import json
import pandas as pd
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
# flash, g, redirect, request, url_for
from nlpnews import analysis, entity

with open('.env', 'r') as filein:
    URL_PREFIX = filein.read().splitlines()[0]

db = SQLAlchemy()

def create_app(test_config=None):
    

    app = Flask(__name__,
                instance_relative_config=True,
                static_folder="static")

    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" +
            os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    app.config['CACHE_TYPE'] = 'simple'
    cache = Cache(app)
    cache.init_app(app)

    migrate = Migrate(app, db)

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    print(f"Flask app instance path set to {app.instance_path}")

    db.init_app(app)
#    from . import models
#    app.cli.add_command(models.init_db_command)

    from . import newsloader
    app.cli.add_command(newsloader.refresh_news_command)
    app.cli.add_command(newsloader.get_totals_command)
    app.cli.add_command(newsloader.get_content_command)

    @app.route("/")
    @app.route("/index")
    @cache.cached(timeout=600)  # cache this view for 10 minutes
    def index():
        bar = analysis.plot_freqs()
        data = analysis.get_most_common_terms()        
        return render_template('index.html', plot=bar, tabledata=data)

    @app.route("/lda/")
    @cache.cached(timeout=600)  # cache this view for 10 minutes
    def lda():
        news_topics = pd.read_csv('./dataframes/newstopics.csv')
        news_topics_words = []
        for i in news_topics.index: 
            news_topics_words.append(" ".join(list(news_topics.iloc[i])[1:])) 

        op_topics = pd.read_csv('./dataframes/opiniontopics.csv')
        op_topics_words = []
        for i in op_topics.index: 
            op_topics_words.append(" ".join(list(op_topics.iloc[i])[1:])) 

        lda_jaccard = pd.read_csv('./dataframes/lda.csv')
        tabledata = []
        
        for i in lda_jaccard.index: 
            row = []
            for j in range(1,4):
                row.append(lda_jaccard.iloc[i][j]) 
            tabledata.append(row)


        data = pd.read_csv('./dataframes/lda_most_common.csv')
        wordcount = list(zip(data['token'], data['count']))

        return render_template("lda.html",  opwords=op_topics_words,
                                            newswords=news_topics_words,
                                            wordcount=wordcount,
                                            tabledata=tabledata,
                                           )

    @app.route("/similarities/")
    @cache.cached(timeout=600)  # cache this view for 10 minutes
    def similarities():
        #src = analysis.plot_jaccard()
        data = pd.read_csv('./dataframes/jaccard.csv')

        tabledata = []
        tabledata.append(list(data.columns[1:]))
        
        for i in data.index: 
            row = []
            for j in range(1, len(data.columns)): 
                row.append(data.iloc[i][j]) 
            tabledata.append(row)

        data = pd.read_csv('./dataframes/jaccard_most_common.csv')
        wordcount = list(zip(data['token'], data['count']))

        return render_template("similarities.html", tabledata=tabledata, wordcount=wordcount)


    @app.route("/entities/")
    @cache.cached(timeout=600)  # cache this view for 10 minutes
    def entities():
        srcbar = analysis.plot_entitybars()
        data = pd.read_csv('./dataframes/entities.csv')
        tabledata = list(zip(data['token'], data['count']))

        plot_layout = { 'title': 'Entities near negative expressions',
                        'height': 1200,
                        'font': {
                            'size': 9,
                            }
                        }

        return render_template("entities.html", plot=srcbar, tabledata=tabledata, plot_layout=plot_layout)


    @app.route(f"/sentiments/")
    @cache.cached(timeout=600)  # cache this view for 10 minutes
    def sentiments():
        srcbar = analysis.plot_sentimentbar()
        srcbar_layout = {'yaxis': {'title': {'text': "Score"},
                                'range': [-10, 20]
                        },
                        'title': 'Compound Scores per Source (note: possible range from -100 to 100', }
        
        srcbar_layout = json.dumps(srcbar_layout)

        scatter = analysis.plot_sentimentscatter2()
        scatter_layout = {'yaxis': {'title': {'text': "Score"},
                        },
                        'title': 'Sentiment scores for all citations in all texts',
                        'height': 700, }
        
        opinions = analysis.plot_opinionscatter()
        opinion_layout = {'yaxis': {'title': {'text': "Score"},
                        },
                        'title': 'Sentiment scores for opinion articles',
                        'height': 600, }        

        popinions = analysis.plot_popinionscatter()
        popinion_layout = {'yaxis': {'title': {'text': "Score"},
                        },
                        'title': 'Sentiment scores for opinion articles, per paragraph',
                        'height': 600, }

        articlescatter = analysis.plot_articlescatter()
        articlescatter_layout = {'yaxis': {'title': {'text': "Score"},
                        },
                        'title': 'Sentiment scores for news articles',
                        'height': 600, }        


        return render_template('sentiments.html',
                                src_plot=srcbar,
                                src_plot_layout=srcbar_layout,
                                src_scatter=scatter,
                                src_scatter_layout=scatter_layout,
                                src_opinions=opinions,
                                src_opinions_layout=opinion_layout,
                                src_popinions=popinions,
                                src_popinions_layout=popinion_layout,
                                src_articles=articlescatter,
                                src_articles_layout=articlescatter_layout,
                                )

    return app

app = create_app()

if __name__ == "__main__":
    app.run()
