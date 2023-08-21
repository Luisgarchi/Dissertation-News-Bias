# https://github.com/richardpaulhudson/coreferee#model-performance

from opennews.pygooglenews import GoogleNews
from opennews.nlptools import url_google_to_original
from newsplease import NewsPlease
from pprint import pprint
from collections import Counter

import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag



import spacy
import spacy_experimental
from spacy import displacy


nlp_coref = spacy.load("en_coreference_web_trf")


article = NewsPlease.from_url('https://edition.cnn.com/2023/08/11/americas/ecuador-villavicencio-assassination-suspects-colombian-intl-hnk/index.html')
text = article.maintext

doc = nlp_coref(text)

pprint(doc.spans)








"""

COREFEREEE

nlp = spacy.load('en_core_web_trf')
nlp.add_pipe('coreferee')


article = NewsPlease.from_url('https://edition.cnn.com/2023/08/11/politics/trump-trial-date-2024-campaign/index.html')

text = article.maintext

print(text)

doc = nlp(text)
items = [x.text for x in doc.ents]
pprint(Counter(items).most_common(3))
doc._.coref_chains.print()
displacy.serve(doc, style="ent")
"""












def posprocess(sentence):
    tokenized = word_tokenize(sentence)
    pos_tagged = pos_tag(tokenized)
    return pos_tagged

def nouns(pos_tagged):
    is_noun = lambda pos: pos[:2] == 'NN'
    return [word for (word, pos) in pos_tagged if is_noun(pos)]




class Title:
    def __init__(self, title):
        self.data = title
        self.pos = posprocess(self.data)
        self.nouns = nouns(self.pos)


class GN_Article:
    def __init__(self, title, url):
        self.title, self.publisher = self.parse_title_publisher(title)
        self.url = url

    def parse_title_publisher(self, title):
        
        def find_split(title):
            i = 1
            while i <= len(title):
                if title[-i] == '-':
                    return len(title) - i
                i += 1

        split_at = find_split(title)

        return Title(title[:split_at].strip()), title[split_at + 1:].strip()

    def __eq__(self, other):
        return self.url == other.url

    def __repr__(self) -> str:
        return f"{self.publisher}: {self.title.data}"

def grabHeadlines():
    publisher_country = ['US', 'UK']
    topics            = ['WORLD', 'NATION']

    news = []
    for country in publisher_country: 
        gn =  GoogleNews(lang = 'en', country = country)

        for topic in topics: 
            articles = gn.topic_headlines(topic)["entries"]
            for article in articles:
                data = GN_Article(article['title'], url_google_to_original(article['link']))
                
                if data not in news:
                    news.append(data)
    
    return news
