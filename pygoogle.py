from pygooglenews import GoogleNews
import newspaper
import requests
import json
import time
import base64


def get_original_url(google_url):
    # https://stackoverflow.com/questions/70658064/retrieve-reformatted-url-from-webpage

    # Set cookie consentement and DON'T USER User-Agent
    cookies = {'CONSENT': 'YES+cb.20210720-07-p0.en+FX+410'}
    response = requests.head(google_url, cookies=cookies, allow_redirects=True)
    return response.history[-1].url

def parse_parse_article(url):
    article = newspaper.Article(url=url, language='en')
    article.download()
    article.parse()

def get_article_url(google_url):
    base64_url = google_url.replace("https://news.google.com/rss/articles/","").split("?")[0]
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

"""
myurl = "https://news.google.com/rss/articles/CBMiYmh0dHBzOi8vd3d3LnJldXRlcnMuY29tL3dvcmxkL2FmcmljYS9wcm8tY291cC1wcm90ZXN0cy1uaWdlci13ZXN0LWFmcmljYW4tbGVhZGVycy1tZWV0LTIwMjMtMDctMzAv0gEA?oc=5&hl=en-US&gl=US&ceid=US:en"

cookies = {'CONSENT': 'YES+cb.20210720-07-p0.en+FX+410'}
response = requests.head(myurl, cookies=cookies, allow_redirects=True)
print(response)

"""

gn =  GoogleNews(lang = 'en')
location = gn.top_news()

print(location.keys())
entries = location['entries']

for i, item in enumerate(entries[:15]):
    print(i, ") ", item["link"])
    print(get_original_url(item["link"]))
    url = get_article_url(item["link"])
    print(url)
    print() 




"""
gn = GoogleNews(lang = 'en', country = 'UK')

July23 = gn.search(query = 'spain+election', from_ = '2023-07-23', to_ = '2023-07-25')

entries = July23["entries"]

print(entries[0].keys())

count = 0
for entry in entries:
    count = count + 1
    print(str(count) + ". " + entry["title"] + ", " + entry["published"])
    print(entry["link"])
    time.sleep(0.25)

"""

"""
top = gn.top_news()

entries = top["entries"]
count = 0

for entry in entries:
   count = count + 1
   # print(str(count) + ". " + entry["title"] + entry["published"])
   time.sleep(0.25)

   
"""