import spacy
from spacy import displacy
from newsplease import NewsPlease
from pprint import pprint
from collections import Counter

nlp = spacy.load("en_core_web_lg")
nlp_coref = spacy.load("en_coreference_web_trf")

# use replace_listeners for the coref components
nlp_coref.replace_listeners("transformer", "coref", ["model.tok2vec"])
nlp_coref.replace_listeners("transformer", "span_resolver", ["model.tok2vec"])

# we won't copy over the span cleaner

nlp.add_pipe("coref", source=nlp_coref)
nlp.add_pipe("span_resolver", source=nlp_coref)
nlp.add_pipe('entityfishing', config={"extra_info": True})

print(nlp.pipe_names)


url_1 = 'https://edition.cnn.com/2023/08/13/politics/coffee-county-georgia-voting-system-breach-trump/index.html'

text_1 = NewsPlease.from_url(url_1)

doc = nlp(text_1.maintext)

#print([(ent.text, ent.kb_id_, ent._.dbpedia_raw_result['@similarityScore']) for ent in doc.ents])

pprint(doc.spans)


"""



for ent in doc.ents:
    print((ent.text, ent.label_, ent._.kb_qid, ent._.url_wikidata, ent._.nerd_score, ent.start, ent.end))



print("\n")

candidate_ents = {}
vector_ents_des = {}

for ent in doc.ents:
    if ('Giuliani' in ent.text) and (ent._.kb_qid not in candidate_ents) : 
        candidate_ents[ent._.kb_qid] = ent._.description






class resolved_entities:

    def __init__(self, doc_objet):
        self.entities = []



def contains_ent(lst, ent):
    i = 0
    while i < len(lst):
        if ent in lst[i].text:
            return True
        i += 1

    return False


def clust_num(mystr): 
    return mystr.split("_")[-1]


def filter_head(item):
    return "_".join(item.split("_")[:-1]) == 'coref_head_clusters'

def filter_clusters(item):
    return "_".join(item.split("_")[:-1]) == 'coref_clusters'


coreference_spans_index = [clust_num(item[0]) for item in doc.spans.items() if contains_ent(item[1], 'Giuliani') and filter_head(item[0])]
candidate_clusters = [item for item in doc.spans.items() if item[0].split('_')[-1] in coreference_spans_index and filter_clusters(item[0])]

for cluster in candidate_clusters:
    for ent in cluster[1]:
        print(ent.text, ent._.kb_qid, ent.start, ent.end)

        
"""