import spacy
from spacy import displacy
from newsplease import NewsPlease
from pprint import pprint
from collections import Counter
import re

# Create pipeline
nlp = spacy.load("en_core_web_trf")
nlp.add_pipe('entityfishing', config={"extra_info": True})

nlp_coref = spacy.load("en_coreference_web_trf")

# use replace_listeners for the coref components
nlp_coref.replace_listeners("transformer", "coref", ["model.tok2vec"])
nlp_coref.replace_listeners("transformer", "span_resolver", ["model.tok2vec"])

# we won't copy over the span cleaner
nlp.add_pipe("coref", source=nlp_coref)
nlp.add_pipe("span_resolver", source=nlp_coref)


print(nlp.pipe_names)

# Download article
url_1 = 'https://edition.cnn.com/2023/08/13/politics/coffee-county-georgia-voting-system-breach-trump/index.html'
text_1 = NewsPlease.from_url(url_1).maintext

# Apply NLP
doc = nlp(text_1)


"""
class BasicEntity:
    def __init__(self, name, type, count):
        self.name  = name
        self.type  = type
        self.count = count

    def __repr__(self):
        return f"{self.name}, {self.type}, {self.count}"
"""


class Entity():
    def __init__(self, name, type, count):
        self.name = name
        self.type = type
        self.count = count
        self.kb_candidates = None
        self.kb_id = None
        self.ent_obj = []
        self.head = None
        self.descriptors = []


    def add_knowledge_base_info(self, kb_candidates_info):
        self.kb_candidates = kb_candidates_info

    def add_ent_obj(self, spacy_ent_obj):
        self.ent_obj.append(spacy_ent_obj)
    
    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def set_head(self, head):
        self.head = head

    def get_descriptors(self):
        None

    def __repr__(self):
        return f"{self.name}, {self.type}, {self.count}"
        


class DocResolve:

    def __init__(self, doc, top_x = 5):
        self.doc = doc
        self.ranked_entities = self.ranked_entities(self.doc)
        self.entities = self.merge_entities(self.ranked_entities, top_x)
        
        self.NED_preprocess()



    def ranked_entities(self, doc):
        entities = [(ent.text, ent.label_) for ent in doc.ents]    # ent._.kb_qid
        ent_count = Counter(entities).most_common()

        entities = []
        for ent in ent_count:
            entities.append(Entity(ent[0][0], ent[0][1], ent[1]))

        return entities



    def merge_entities(self, entities, top_x):

        entities_most_common = entities.copy()

        """Establish helper function"""
        def perform_pass_entity_check(ent):
            j = 0
            while entities_most_common and j < len(entities_most_common):
                ent_B = entities_most_common[j]
                if ent.type == ent_B.type and (ent.name in ent_B.name or ent_B.name in ent.name):
                    candidates.append(ent_B)
                    entities_most_common.pop(j)
                    continue
                
                j += 1


        """Return the top_x entities, check for subsets of the same entity"""

        entities = []
        i = 0
        while entities_most_common and i < top_x:

            # Get the top entity
            ent_A = entities_most_common[0]
            entities_most_common.pop(0)

            # test against other entities in the list
            candidates = []
            perform_pass_entity_check(ent_A)

            # perform a second pass check over the list with any candidates found in the previous step
            k = 0
            while candidates and k < len(candidates):
                ent_C = candidates[k]
                perform_pass_entity_check(ent_C)
                k += 1
            
            # Second to last step merge all the candidates with the original candidate (ent_A)
            count = 0
            for candidate in candidates:
                count += candidate.count
            count += ent_A.count

            # Save the merged canidate entity
            entities.append(Entity(ent_A.name, ent_A.type, count))

            # Last step increase the counter by 1
            i += 1
        
        return entities

    

    def kb_preprocess(self):

        for entity in self.entities: 
            count = Counter([(ent._.kb_qid, ent._.description) for ent in doc.ents if (ent.text in entity.name) or (entity.name in ent.text)]).most_common()
            unpack_count = [(candidate[0][0], candidate[0][1], candidate[1]) for candidate in count]
            entity.add_knowledge_base_info(unpack_count)
    

    def get_ent_objs(self):

        for entity in self.entities:
            for ent in self.doc.ents:
                if (entity.name in ent.text) or (ent.text in entity.name):
                    entity.add_ent_obj(ent)


    def get_heads(self):

        for entity in self.entities: 
            """If the name is of length one token then it is the head"""
            words = entity.name.split(' ')
            if len(words) == 1:
                entity.set_head(entity.name)

            # Otherwise find the most likely head
            else:
                for ent in entity.ent_obj:

                    candidate_head = {}

                    for word in words:
                        candidate_head[word] = 0

                    for token in self.doc[ent.start : ent.end]:
                        for key in candidate_head.keys():
                            if token.head.text == key:
                                candidate_head[key] += 1

                    head = max(candidate_head, key = candidate_head.get)
                    entity.set_head(head)



    def NED_preprocess(self):

        self.kb_preprocess()
        self.get_ent_objs()
        self.get_heads()
        # entities = self.get_descriptors(entities)
    





        







mydoc = DocResolve(doc)

for ent in mydoc.ranked_entities:
    print(ent)
print()


for ents in mydoc.entities:
    for ent in ents.ent_obj:
        print(ent.text, ent.start, ent.end, [(token.text, token.pos_, token.dep_, token.head) for token in doc[ent.start : ent.end]])

print()
for ent in mydoc.entities:
    print(ent.head)



"""
    THROW AWAY ents THAT ARE NOT PROPER NOUNS
    KEEP ONLY nsubj, pobj, dobj
    Store compounds
"""


"""
myents = [ent.name for ent in mydoc.merge_entities]
print(myents)

print()
for ent in myents:
    pprint([chunk.text for chunk in doc.noun_chunks if ent in chunk.root.text])
    print()
"""

"""
for ent in myents: 
    pprint([(token.text, token.dep_, token.head.text) for token in doc if ent in token.head.text])
"""

"""

pprint(doc.spans)

deps = ['nsubj', 'dobj', 'pobj']
pos_noun = ['NOUN', 'PROPN']
for ent in myents: 
    for token in doc: 
        if (token.text in ent or ent in token.text) and token.dep_ in deps:
                if token.pos_ in pos_noun:
                    print(token.text, token.pos_, token.head.text, token.head.pos_)


for ent in myents: 
    for token in doc: 
        if (token.text in ent or ent in token.text):
                print(token.text, token.pos_, token.head.text, token.head.pos_)


"""