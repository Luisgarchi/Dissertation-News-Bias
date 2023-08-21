import spacy
from newsplease import NewsPlease
from pprint import pprint
from

# Download article
url = 'https://edition.cnn.com/2023/08/13/politics/coffee-county-georgia-voting-system-breach-trump/index.html'
text = NewsPlease.from_url(url).maintext

nlp = spacy.load('en_coreference_web_trf')

print(nlp.pipe_names)

doc = nlp(text)

pprint(doc.spans)

"""
import spacy
from spacy import displacy
from newsplease import NewsPlease
from pprint import pprint
from collections import Counter

# Create pipeline
nlp = spacy.load("en_core_web_trf")
#nlp.add_pipe('entityfishing', config={"extra_info": True})

# Download article
url_1 = 'https://edition.cnn.com/2023/08/13/politics/coffee-county-georgia-voting-system-breach-trump/index.html'
text_1 = NewsPlease.from_url(url_1).maintext

# Apply NLP
doc = nlp(text_1)

# Get the top X = 5 Entities
entities = [(ent.text, ent.label_, ent._.kb_qid) for ent in doc.ents]
ranked_entities = Counter(entities).most_common()
"""