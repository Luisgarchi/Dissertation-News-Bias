from pygooglenews import GoogleNews
from nlptools import get_publisher_from_url, url_google_to_original
import newspaper
import validators
import datetime

def globalNews():

    """Get the top news articles from goolge news"""

    # Use pygooglenews to get the top articles
    gn =  GoogleNews(lang = 'en')
    gn_news = gn.top_news()['entries']

    articles = proccessGoogleNews(gn_news)

    return articles


def publisherLocationNews(location):
    return None

def geographicLocationNews(geographic):
    return None


def proccessGoogleNews(gn_news):

    # Get the urls
    urls = []
    for article in gn_news:
        publisher_url = url_google_to_original(article["link"])

        # Check if valid url
        if validators.url(publisher_url):
            urls.append(publisher_url)

    # Extract information
    articles = []
    for url in urls:

        try: 
            article = newspaper.Article(url=url, language='en')
            article.download()
            article.parse()
        except:
            continue

        # Convert to dictionary and drop unnessary attributes
        tidy_article = filter_article_attributes(article)
        articles.append(tidy_article)
    
    return articles



def filter_article_attributes(article_obj):


    article = {
        "title": str(article_obj.title),
        "text": str(article_obj.text),
        "published_date": str(article_obj.publish_date),
        "summary": str(article_obj.summary),
        "url" : str(article_obj.url),
        "publisher": get_publisher_from_url(article_obj.url)
    }

    return article




