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

sources = []

def read_data():
    with open('articles.json', 'r') as filein:
        sources_in = filein.read()
        sources_in = json.loads(sources_in)
    return sources_in

def write_data():
    with open('articles.json', 'w') as fileout:
        fileout.write(json.dumps(sources))


def write_rss():
    with open('rss_entries.json', 'w') as fileout:
        fileout.write(json.dumps(feed_entries))


def read_rss():
    with open('rss_entries.json', 'r') as filein:
        rss_in = filein.read()
        rss_in = json.loads(rss_in)
    return rss_in




@click.command("refresh_news")
@with_appcontext
def refresh_news_command():
    """ Refreshes news from command line"""
    #refresh_news()
    click.echo('News refreshed.')


@click.command("get_totals")
@with_appcontext
def get_totals_command():
    """ Get total number of news articles fetched"""
    sources = read_data()
    
    click.echo('News refreshed.')



