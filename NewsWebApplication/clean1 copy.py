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

class Entity():
    def __init__(self, name, type, count):
        self.name = name
        self.type = type
        self.count = count
        self.kb_candidates = None
        self.kb_id = None
        self.ent_obj = []
        self.ent_spans = []
        self.head = None
        self.descriptors = []
        self.coref_clusters = []

    def add_knowledge_base_info(self, kb_candidates_info):
        self.kb_candidates = kb_candidates_info

    def add_ent_obj(self, spacy_ent_obj, span):
        self.ent_obj.append(spacy_ent_obj)
        self.ent_spans.append(span)

    def set_head(self, head):
        self.head = head

        for ent in self.ent_spansy:
            self.add_descriptor(ent, self.head)


    def add_descriptor(self, span, head):

        # str -> None

        # x = ['PROPN', 'NOUN', 'ADJ']
        for token in span:
            if token.head.text == head and token.dep_ == 'compound' and token.text not in self.descriptors:
                self.ent_obj.append(token.text)


    def add_chunk_descriptors(self, chunk):

        # span -> None

        for token in chunk:
            if token.text != self.head:
                self.add_descriptors(token.text)

    def add_coreference_clusters(self, cluster):
        self.coref_clusters.extend(cluster)



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

    

    def kb_preprocess(self, entity):

        count = Counter([(ent._.kb_qid, ent._.description) for ent in doc.ents if (ent.text in entity.name) or (entity.name in ent.text)]).most_common()
        unpack_count = [(candidate[0][0], candidate[0][1], candidate[1]) for candidate in count]
        entity.add_knowledge_base_info(unpack_count)
    

    def get_ent_objs(self, entity):

        for ent in self.doc.ents:
            if (entity.name in ent.text) or (ent.text in entity.name):
                span = doc[ent.start:ent.end]
                entity.add_ent_obj(ent, span)


    def get_heads(self, entity):

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



    def get_descriptors(self, entity):
        """Maybe can take in an argument as well with potential descriptors of the previous get_heads"""
        """Can also use the coreferences resolved that are not prononuns e.g. modofies"""
        """Use chunks as well"""

        for ent in entity.ent_obj:

            for token in self.doc[ent.start : ent.end]:
                if token.head.text == entity.head and token.dep_ == 'compound':
                    entity.add_descriptors(token.text)


        # Check noun phrases that can describe the ent
        for chunk in self.doc.noun_chunks:
            if entity.head in chunk.root.text:
                entity.add_chunk_descriptors(chunk)




    def get_coref_clusters(self):
        """Helper function"""
        def heads_in_cluster(entities, cluster):

            # (list, list) -> True
            heads = [entity.head for entity in entities]
            for coref in cluster:
                if coref.text in heads:
                    return True
            return False
        

        entities_obj_map = {entity.name: entity for entity in self.entities}
        
        coref_clusters = {
            key: coref for key, coref in self.doc.spans.items() 
            if re.match(r"coref_head_clusters_*", key)
            and heads_in_cluster(self.entities, coref)
            }

        for coref_span in coref_clusters.items():
            key, coreferences = coref_span[0], coref_span[1]
            key = key.split('_')[-1]

            coref_candidates = {}
            for entity in self.entities:
                for reference_head in coreferences:
                    if entity.head in reference_head.text:
                        if entity.name not in coref_candidates:
                            coref_candidates[entity.name] = 1
                        else:
                            coref_candidates[entity.name] += 1
                    #Pronouns are ignored since we are only interested in finding mentions of the found entities
                

            if len(coref_candidates) == 1:
                # There is only one associated coreference cluster
                associated_entity = list(coref_candidates.keys())[0]
                cluster_key = 'coref_clusters_' + key
                entities_obj_map[associated_entity].add_coreference_clusters(self.doc.spans[cluster_key])
            else: 
                # If there is more than one entity in the span we need to find the most common head 
                # Pronouns are assign to the most common entity
                # Other head mentions are added to their respective entiity

                most_common_entity = max(coref_candidates, key = coref_candidates.get)
                cluster_key = 'coref_clusters_' + key
                
                other_ents = list(coref_candidates.keys())
                other_ents.remove(most_common_entity)

                
                for i, reference_head in enumerate(coreferences):
                    for entity_name in other_ents:
                        
                        #Get the coreference span in question
                        reference_span = [self.doc.spans[cluster_key][i]]
                        """Potential Bug"""
                        # If it is the head or a descriptor (typically compound dependecy) of another entity add the coreference span to that entity
                        if reference_head.text == entities_obj_map[entity_name].head or reference_head.text in entities_obj_map[entity_name].descriptors:
                            entities_obj_map[entity_name].add_coreference_clusters(reference_span)
                        else: 
                            # Otherwise Save it to the most common
                            entities_obj_map[most_common_entity].add_coreference_clusters(reference_span)
        


    def NED_preprocess(self):

        for entity in self.entities:

            self.kb_preprocess(entity)
            self.get_ent_objs(entity)
            self.get_heads(entity)
            # self.get_descriptors(entity) # Need to prevent adding pronouns might get in the way of coreference resolution
        
        
        coreference_clusters = self.get_coref_clusters()
    



"""
Bug ticket - for DocResolve.get_coref_clusters()
What if there are two or more entities that has the same head, e.g. Coffee County and Fulton County

How can we match the coreference clusters to each one? - Use the coref_cluster spans instead of the coref_head_clusters.
"""


"""
Split get descriptors into two methods one for, compound dependencies of the head and another for chunk descriptors

Create associated entity method on doc resolve

filter the descriptors to add only PROPN, NOUN (if PROPN then check for asociated entities) and ADJ if token head is the the orgingial head of coref

1. Check for new potential heads to add to descriptors,
2.
- Check the cluster spans for adjectives that describe the head
- Check for other entities that are associated to the head
    - Get the head of the span (we can use coref_cluster_heads, check for other PROPN/NOUNs that are not the entity in question and that have the head of the cluster as the token.head)
    - Optional check if the entity is one of the detected ones already (if this is the case the method must be in the DocResolve class and not the Entity class)
- Remove capitals for personal Nouns

"""






mydoc = DocResolve(doc, top_x = 5)

"""
for ents in mydoc.entities:
    for ent in ents.ent_obj:
        print(ent.text, ent.start, ent.end, [(token.text, token.pos_, token.dep_, token.head) for token in doc[ent.start : ent.end]])
"""


print()
for ent in mydoc.entities:
    print(ent.head, ": ", ent.descriptors)





print()
for ent in mydoc.entities:
    print(ent.head, ": \n")
    for item in ent.coref_clusters:
        print([(token.text, token.pos_, token.dep_, token.head.text) for token in item])

"""

pprint(doc.spans)

"""







"""
    THROW AWAY ents THAT ARE NOT PROPER NOUNS
    KEEP ONLY nsubj, pobj, dobj
    Store compounds
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