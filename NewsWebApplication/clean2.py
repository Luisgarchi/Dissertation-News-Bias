import spacy
from spacy import displacy
from newsplease import NewsPlease
from pprint import pprint
from collections import Counter
import re

nlp = spacy.load("en_core_web_trf")

print(nlp.pipe_names)

# Download article
url_1 = 'https://edition.cnn.com/2023/08/13/politics/coffee-county-georgia-voting-system-breach-trump/index.html'
text_1 = NewsPlease.from_url(url_1).maintext

doc = nlp(text_1)


pprint([(ent.text, ent.start, ent.end, ent.sentiment) for ent in doc.ents])