import spacy
from pprint import pprint
from spacy import displacy
from spacy.tokens import Span
from collections import Counter
from spacy.symbols import nsubj, VERB
from pygooglenews import GoogleNews
from nlptools import url_google_to_original
from newsplease import NewsPlease
import re

text = "Atlanta-area prosecutors investigating efforts to overturn the 2020 election results in Georgia are in possession of text messages and emails directly connecting members of Donald Trump’s legal team to the early January 2021 voting system breach in Coffee County, sources tell CNN."

nlp = spacy.load("en_core_web_trf")
nlp_coref = spacy.load("en_coreference_web_trf")

# use replace_listeners for the coref components
nlp_coref.replace_listeners("transformer", "coref", ["model.tok2vec"])
nlp_coref.replace_listeners("transformer", "span_resolver", ["model.tok2vec"])

# we won't copy over the span cleaner
nlp.add_pipe("coref", source=nlp_coref)
nlp.add_pipe("span_resolver", source=nlp_coref)

doc = nlp(text)

verbs = set()
for possible_subject in doc:
    if possible_subject.dep == nsubj and possible_subject.head.pos == VERB:
        verbs.add(possible_subject.head)
print(verbs)