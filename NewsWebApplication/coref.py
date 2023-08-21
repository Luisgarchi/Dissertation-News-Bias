import spacy
from newsplease import NewsPlease
from pprint import pprint


# Download article
url = 'https://edition.cnn.com/2023/08/13/politics/coffee-county-georgia-voting-system-breach-trump/index.html'
text = NewsPlease.from_url(url).maintext

nlp = spacy.load("en_core_web_trf")
nlp_coref = spacy.load("en_coreference_web_trf")

# use replace_listeners for the coref components
nlp_coref.replace_listeners("transformer", "coref", ["model.tok2vec"])
nlp_coref.replace_listeners("transformer", "span_resolver", ["model.tok2vec"])

# we won't copy over the span cleaner
nlp.add_pipe('entityfishing', config={"extra_info": True})
nlp.add_pipe("coref", source=nlp_coref)
nlp.add_pipe("span_resolver", source=nlp_coref)


print(nlp.pipe_names)

doc = nlp(text)

trump_mentions = []
for ref in doc.spans['coref_clusters_8']:
    print((ref.text, ref.start, ref.end))
    trump_mentions.append([ref.text, ref.start, ref.end])


stitch = []
for ent in doc.ents:
    if [ent.text, ent.start, ent.end] in trump_mentions:
        stitch.append([ent.text, ent.start, ent.end, ent.label_, ent._.kb_qid, ent._.url_wikidata, ent._.nerd_score])
        print((ent.text, ent.label_, ent._.kb_qid, ent._.url_wikidata, ent._.nerd_score, ent.start, ent.end))



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