from pygooglenews import GoogleNews
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
    gn =  GoogleNews(lang = 'en')
    location = gn.top_news()

def publisherLocationNews(location):

def geographicLocationNews(geographic):
    