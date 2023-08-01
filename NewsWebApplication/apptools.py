from pygooglenews import GoogleNews
from nlptools import get_publisher_from_url
import newspaper
import base64


def parse_parse_article(url):
    article = newspaper.Article(url=url, language='en')
    article.download()
    article.parse()

def get_article_url(google_url):

    # https://stackoverflow.com/questions/76082944/how-to-collect-the-url-from-the-clicked-article-instead-of-the-google-news-site

    base64_url = google_url.replace("https://news.google.com/rss/articles/","").split("?")[0]
    
    # https://gist.github.com/perrygeo/ee7c65bb1541ff6ac770

    pad = len(base64_url) % 4
    base64_url_pad = f"{base64_url}{'=' * pad}"
    print(pad)
    actual_url = base64.b64decode(base64_url_pad)[4:].decode('latin-1')
    if 'Ò' in actual_url:
        urls = actual_url.split("Ò")
        urls[1] = urls[1][2:]
        return urls
    else:
        return [actual_url]
    

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
        publisher_url = get_article_url(article["link"])[0]
        urls.append(publisher_url)

    # Extract information
    articles = []
    for url in urls:
        article = newspaper.Article(url=url, language='en')
        article.download()
        article.parse()

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