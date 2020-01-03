"""
All kinds of helper functions for retrieving, parsing, cleaning and storing articles.
Most are copied directly from Jupyter Notebook, reflecting the process of manually
triggering different operations. These can and should be used from python IDLE.
"""

import os
import re
from datetime import datetime
import json
import string
import uuid
import click

import pandas as pd 
import numpy as np
from newsapi import NewsApiClient
from newspaper import Article as artsu
from flask.cli import with_appcontext

# Create News Api Client
with open('newsapikey.txt', 'r') as filein:
    newsapikey = filein.read().strip()
newsapi = NewsApiClient(api_key=newsapikey)

# Read existing article sources from files

urls_to_ignore = [
    '/review/',
    '/interactive/',
    '/programmes/',
    '/video/',
    '/in-pictures-',
    '/v/',
    '/programs/',
    '/arts/television/',
    '/av/',
]

''' Match certain url patterns to ignore irrelevant articles '''
def should_ignore(url):
    for ignore in urls_to_ignore:
        if url.find(ignore) != -1:
            return True
    return False


# Cleanup
remove_if_found = [
    r'^Shape Created',
    r'^Please enable cookies',
    r'^Independent news email',
    r'^Download the new',
    r'^We use cookies',
    r'^CLICK HERE',
    r'^Image copyright',
    r'^Image caption',
    r'^The new European data protection law requires us',
    r'^Media playback is unsupported',
    r'^Follow .* Twitter',
]

def cleanup(content):
    newlines = []
    artlines = content.splitlines()
    for line in artlines:
        keep_line = True
        # Make individual checks of the line
        if line.isupper():
            keep_line = False
        elif len(line) < 5:
            keep_line = False        
        else:
            for to_remove in remove_if_found:
                if len(re.findall(to_remove, line)) != 0:
                    keep_line = False
                    continue           
        if keep_line:
              newlines.append(line)
    return "\n".join(newlines)


def reprocess(sources, and_delete=True):
    new_sources = {}
    for src in sources.keys():
        keepers = []
        for i, article in enumerate(sources[src]):
            if should_ignore(article['url']):
                print(f"To delete: {src}, {i}, url: {article['url']}")                
            else:
                 keepers.append(article)
            
        if and_delete == True:
            print("Deleting selected items.")
            new_sources[src] = keepers
        else:
            print("This was a dry run. No items were deleted.")
            pass
    
    if and_delete == True:
        return new_sources
    else:
        return sources


''' Get all new articles matching Thunberg and Climate (not very reusable here...)'''
def get_articles(permanent=True):
    sources = read_data()

    # Use urls as unique identifiers to spot existing articles
    urls = []
    for src in sources.keys():
        for art in sources[src]:
            urls.append(art['url'])
            
    for src in sources.keys():
        result_page = 1
        retrieved_nr = 0
        articles = []
        
        # Page through if there are more than 20 articles
        while 1:
            result = newsapi.get_everything(q='Thunberg AND climate',
                                            sources=src,
                                            page=result_page)
            retrieved = result['articles']
            retrieved_nr += len(retrieved)
            articles += retrieved
            if result['totalResults'] > retrieved_nr:
                result_page += 1
            else:
                break
                
        new_articles = []
        dups = 0
        ignored = 0
        for art in articles:
            if art['url'] in urls:
                dups += 1
            elif should_ignore(art['url']):
                ignored += 1
            else:
                art['uuid'] = str(uuid.uuid4())
                new_articles.append(art)
        print(f"{src}: {len(articles)} articles retrieved, {dups} existing, {ignored} ignored.")
        sources[src] += new_articles
    
    if permanent:
        write_data(sources)

def get_content_for(uuid):
    sources = read_data()
    for src in sources:
        for article in sources[src]:
            if article['uuid'] == uuid:
                with open(f"./articlecontent/{uuid}", "r") as filein:
                    content = filein.read()
                return content


def get_content(url):
    try:
        newarticle = artsu(url)
        print(f"Downloading Article from: {url}")
        newarticle.download()
        newarticle.parse()
    except:
        print("Unexpected error occurred")
    else:     
        return newarticle.title + "\n\n" + newarticle.text
    

def get_new_content():
    ''' Retrieve the actual article content, cleanup and store in file'''
    
    existing = os.listdir('./articlecontent/')
    sources = read_data()

    for src in sources.keys():
        for article in sources[src]:
            if article['uuid'] in existing:
                pass
            else:
                print('downloading new: ', article['uuid'])
                new_article = get_content(article['url'])
                new_article = cleanup(new_article)
                with open(f"./articlecontent/{article['uuid']}", "w") as fileout:
                    fileout.write(new_article)


def read_data():
    with open('articles.json', 'r') as filein:
        sources_in = filein.read()
        sources_in = json.loads(sources_in)
    return sources_in

def write_data(sources_to_write):
    with open('articles.json', 'w') as fileout:
        fileout.write(json.dumps(sources_to_write))


def write_rss():
    with open('rss_entries.json', 'w') as fileout:
        fileout.write(json.dumps(feed_entries))


def read_rss():
    with open('rss_entries.json', 'r') as filein:
        rss_in = filein.read()
        rss_in = json.loads(rss_in)
    return rss_in

def get_citations(article):
    citations = []
    art = get_content_for(article['uuid'])
    for line in art.splitlines():
        pass

def get_totals():
    sources = read_data()
    for src in sources.keys():
        print(f"{src:20}: {len(sources[src]):4} articles")


@click.command("refresh_news")
@with_appcontext
def refresh_news_command():
    """ Refreshes news from command line"""
    get_articles()
    click.echo('News refreshed.')

@click.command("get_content")
@with_appcontext
def get_content_command():
    """ Gets content to new articles """
    get_new_content()
    click.echo('News refreshed.')


@click.command("get_totals")
@with_appcontext
def get_totals_command():
    """ Get total number of news articles fetched"""
    get_totals()
    click.echo('Done.')



