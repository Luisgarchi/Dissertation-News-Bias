"""import spacy
from spacy import displacy
import spacy_dbpedia_spotlight


nlp = spacy.load("en_core_web_trf")
nlp_coref = spacy.load("en_coreference_web_trf")

# use replace_listeners for the coref components
nlp_coref.replace_listeners("transformer", "coref", ["model.tok2vec"])
nlp_coref.replace_listeners("transformer", "span_resolver", ["model.tok2vec"])

# we won't copy over the span cleaner
nlp.add_pipe("coref", source=nlp_coref)
nlp.add_pipe("span_resolver", source=nlp_coref)
nlp.add_pipe('dbpedia_spotlight')
print(nlp.pipe_names)"""

from newsplease import NewsPlease
from pprint import pprint
from collections import Counter
import spacy

nlp = spacy.load("en_core_web_trf")
nlp = spacy.load("en_core_web_trf")
nlp_coref = spacy.load("en_coreference_web_trf")

# use replace_listeners for the coref components
nlp_coref.replace_listeners("transformer", "coref", ["model.tok2vec"])
nlp_coref.replace_listeners("transformer", "span_resolver", ["model.tok2vec"])

# we won't copy over the span cleaner
nlp.add_pipe("coref", source=nlp_coref)
nlp.add_pipe("span_resolver", source=nlp_coref)

#nlp.add_pipe('dbpedia_spotlight', config={'verify_ssl': False})

url_1 = 'https://edition.cnn.com/2023/08/13/politics/coffee-county-georgia-voting-system-breach-trump/index.html'

text_1 = NewsPlease.from_url(url_1)

doc = nlp(text_1.maintext)
#print([(ent.text, ent.kb_id_, ent._.dbpedia_raw_result['@similarityScore']) for ent in doc.ents])


print("\n")
items = [(ent.text, ent.label_) for ent in doc.ents]
pprint(Counter(items).most_common(15))