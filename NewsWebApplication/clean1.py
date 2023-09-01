import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
from newsplease import NewsPlease
from pprint import pprint
from collections import Counter
import re
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')


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


nlp.add_pipe('spacytextblob')

print(nlp.pipe_names)

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
        self.chunk_descriptors = []
        self.adjectives = []
        self.related_entities = []
        self.coref_spans = []
        self.coref_heads = []

    def add_knowledge_base_info(self, kb_candidates_info):
        self.kb_candidates = kb_candidates_info
        print(kb_candidates_info)

    def resolve_kb_candidates(self):

        # Case 1) There is only one candidate - assign the caniddate as the knowledge base ID - kb_id
        if len(self.kb_candidates) == 1:
            self.kb_id = list(self.kb_candidates.keys())[0]

        elif len(self.kb_candidates)> 1:
            
            # if the entity is of type person filter candidate for wikidata instance of human (Q5)
            if self.type == 'PERSON':

                delete_keys = []
                for can_key in self.kb_candidates.keys():
                    if self.kb_candidates[can_key]['instance'] not in ['Q5', None]:
                        delete_keys.append(can_key)
                
                for del_key in delete_keys:
                    del self.kb_candidates[del_key] 

            key_words = [self.head]
            extend_list = [self.descriptors, self.related_entities, self.adjectives, self.chunk_descriptors]
            for extend in extend_list:
                key_words.extend(extend)

            key_words = set([word.lower() for word in key_words])
            
            for can_key in self.kb_candidates.keys():
                self.kb_candidates[can_key]['desc_doc'] = nlp(self.kb_candidates[can_key]['description'])
                sentences = [x for x in self.kb_candidates[can_key]['desc_doc'].sents]
                first_sentence = sentences[0].text

                tokenized_words = tokenize_number_words(remove_punctuation(first_sentence), 50, sw)
                self.kb_candidates[can_key]['tokenized'] = unique_maintain_order(tokenized_words)

                score = 0
                for token in self.kb_candidates[can_key]['tokenized']:
                    if token in key_words:
                        score += 1
                
                self.kb_candidates[can_key]['score'] = score

            heighest_score = 0
            best_key = ''
            for can_key in self.kb_candidates.keys():
                if self.kb_candidates[can_key]['score'] > heighest_score:
                    heighest_score = self.kb_candidates[can_key]['score']
                    best_key = can_key

            self.kb_id = best_key



    def add_ent_obj(self, spacy_ent_obj):
        self.ent_obj.append(spacy_ent_obj)
    
    def add_descriptor(self, descriptor):
        if descriptor not in self.descriptors and descriptor not in self.head:
            self.descriptors.append(descriptor)

    def set_head(self, head):
        self.head = head

    def add_chunk_descriptor(self, descriptor):
        if (descriptor not in self.chunk_descriptors 
            and descriptor not in self.adjectives 
            and descriptor not in self.descriptors 
            and descriptor not in self.head):
            self.chunk_descriptors.append(descriptor)
    
    def add_adjective(self, adjective):
        if adjective not in self.adjectives:
            self.adjectives.append(adjective)

    def add_related_entity(self, entity_name):
        if entity_name not in self.related_entities:
            self.related_entities.append(entity_name)

    def add_coreference(self, span, head):
        self.coref_spans.append(span)
        self.coref_heads.append(head)

    def __repr__(self):
        return f"{self.name}, {self.type}, {self.count}"
        


def unique_maintain_order(seq):
    # https://stackoverflow.com/questions/480214/how-do-i-remove-duplicates-from-a-list-while-preserving-order
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def remove_punctuation(text):
    
    # Removes punctuation (str -> str)
    
    remove_punctuation = string.punctuation + "‘’’—“”"
    return text.lower().translate(str.maketrans('', '', remove_punctuation))

# We have to remove the punctation from stop words because 
# punctuation will be remove from the text, 
# inorder for them to match they must be processed the same (or removed before)

sw = [remove_punctuation(word) for word in stopwords.words('english')]

def tokenize_number_words(text, number, sw):
    
    # Tokenizes words, removes stop words and returns the first n number of tokens (str -> list)
    
    tokenized = word_tokenize(text)
    
    i = 0
    while i < number and i < len(tokenized):
        if tokenized[i] in sw: 
            del tokenized[i]
        else: 
            i += 1
    
    if number < len(tokenized):
        del tokenized[number:]
    
    return tokenized




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
                if ent.type == ent_B.type and (ent.name.lower() in ent_B.name.lower() or ent_B.name.lower() in ent.name.lower()):
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
        
        """HELPER FUNCTION"""

        def get_instance(properties):

            if not properties:
                return None

            else:
                for property in properties:
                    if property['propertyName'] == 'instance of':
                        return property['value']

        kb_candidates = {}

        for ent in doc.ents:
            if (ent.text.lower() in entity.name.lower()) or (entity.name.lower() in ent.text.lower()):
                if ent._.kb_qid:      # Make sure not None
                    if ent._.kb_qid not in kb_candidates:
                        kb_candidates[ent._.kb_qid] = {}
                        kb_candidates[ent._.kb_qid]['count'] = 1
                        kb_candidates[ent._.kb_qid]['description'] = ent._.description
                        kb_candidates[ent._.kb_qid]['instance'] = get_instance(ent._.other_ids)
                    else:
                        kb_candidates[ent._.kb_qid]['count'] += 1

        
        #count = Counter([(ent._.kb_qid, ent._.description) for ent in doc.ents if (ent.text.lower() in entity.name.lower()) or (entity.name.lower() in ent.text.lower())]).most_common()
        #unpack_count = [(candidate[0][0], candidate[0][1], candidate[1]) for candidate in count]
        entity.add_knowledge_base_info(kb_candidates)
    

    def get_ent_objs(self, entity):

        for ent in self.doc.ents:
            if (entity.name.lower() in ent.text.lower()) or (ent.text.lower() in entity.name.lower()):
                entity.add_ent_obj(ent)


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
                entity.set_head(head.capitalize())


    def get_ner_descriptors(self, entity):
        """Maybe can take in an argument as well with potential descriptors of the previous get_heads"""
        """Can also use the coreferences resolved that are not prononuns e.g. modofies"""
        """Use chunks as well"""

        for ent in entity.ent_obj:

            for token in self.doc[ent.start : ent.end]:
                if token.head.text.lower() == entity.head.lower() and token.dep_ == 'compound':
                    entity.add_descriptor(token.text.capitalize())


        # Check noun phrases that can describe the ent
        for chunk in self.doc.noun_chunks:
        
            if entity.name.lower() in chunk.text.lower():
                if entity.head in chunk.root.text:
                    for token in chunk:
                        if token.pos_ in ['PROPN', 'NOUN', 'ADJ']:
                            entity.add_chunk_descriptor(token.text)
                

                descriptors = [token.text for token in chunk if token.pos_ in ['PROPN', 'NOUN'] and entity.head.lower() in token.head.text.lower()]
                for descriptor in descriptors:
                    entity.add_descriptor(descriptor)

                adjectives = [token.text for token in chunk if token.pos_ in ['ADJ'] and entity.head.lower() in token.head.text.lower()]
                for adjective in adjectives:
                    entity.add_adjective(adjective)
                    

    def get_coref_clusters(self):

        """Helper function"""

        def heads_in_cluster(entities, cluster):
            # (list, list) -> True
            heads = [entity.head for entity in entities]
            for coref in cluster:
                if coref.text in heads:
                    return True
            return False
        
        # Create a mapping from entity name to an entity object
        entities_obj_map = {entity.name: entity for entity in self.entities}
        
        # Filter the relevant coreference spans. Criteria: 1) Only head clusters. 2) Contains a found entity head 
        coref_clusters = {
            key: coref for key, coref in self.doc.spans.items() 
            if re.match(r"coref_head_clusters_*", key)
            and heads_in_cluster(self.entities, coref)
            }

        for coref_span in coref_clusters.items():

            # Iterate over keys a and values for the filtered clusters 
            key = coref_span[0]
            coreferences = coref_span[1]

            # Get the cluster key number
            key = key.split('_')[-1]

            # Find the respective entity for the coreference groups by using a voting system 
            # if the head of an entity appears in the coreference cluster head
            coref_candidates = {}
            for entity in self.entities:
                for reference_head in coreferences:
                    if entity.head in reference_head.text:
                        if entity.name not in coref_candidates:
                            coref_candidates[entity.name] = 1
                        else:
                            coref_candidates[entity.name] += 1
                    #Pronouns are ignored since we are only interested in finding mentions of the found entities
                
            cluster_key = 'coref_clusters_' + key

            if len(coref_candidates) == 1:
                # There is only one associated coreference cluster
                associated_entity = list(coref_candidates.keys())[0]
                head_key = 'coref_head_clusters_' + key

                self.process_coreference_span(entities_obj_map[associated_entity], self.doc.spans[cluster_key], self.doc.spans[head_key])
            else: 
                # If there is more than one entity in the coref head cluster find the most common head 
                most_common_entity = max(coref_candidates, key = coref_candidates.get)

                # The pronouns of the cluster are assign to the most common entity
                # Other head mentions are added to their respective entiity

                other_ents = list(coref_candidates.keys())
                other_ents.remove(most_common_entity)

                
                for i, reference_head in enumerate(coreferences):
                    for entity_name in other_ents:
                        
                        #Get the coreference span in question
                        reference_span = self.doc.spans[cluster_key][i]
                        """Potential Bug"""
                        # If it is the head or a descriptor (typically compound dependecy) of another entity add the coreference span to that entity
                        if reference_head.text == entities_obj_map[entity_name].head or reference_head.text in entities_obj_map[entity_name].descriptors:
                            self.process_coreference(entities_obj_map[entity_name], reference_span, reference_head)
                        else: 
                            # Otherwise Save it to the most common
                            self.process_coreference(entities_obj_map[most_common_entity], reference_span, reference_head)
    

    def process_coreference_span(self, entity, coref_span, coref_head):

        for i in range(len(coref_span)):
            self.process_coreference(entity, coref_span[i], coref_head[i])


    def process_coreference(self, entity, reference, head):
        

        if head[0].pos_ in ['PROPN','NOUN']:            
            entity.add_descriptor(head.text.capitalize())

        # Check for other entities inside
        other_entities = [ent for ent in self.entities if ent.name != entity.name]

        for other_ent in other_entities:

            for ent_obj in other_ent.ent_obj:
                if ent_obj.start >= reference.start and ent_obj.end <= reference.end:
                    entity.add_related_entity(other_ent.name)

        # Add the coreference
        entity.add_coreference(reference, head)


    def NED_preprocess(self):

        for entity in self.entities:

            self.kb_preprocess(entity)
            self.get_ent_objs(entity)
            self.get_heads(entity)
            self.get_ner_descriptors(entity) # Need to prevent adding pronouns might get in the way of coreference resolution
        
        self.get_coref_clusters()

        for entity in self.entities:
            entity.resolve_kb_candidates()

    #def apply_sentiment_analysis(self):



        

    



"""
Bug ticket - for DocResolve.get_coref_clusters()
What if there are two or more entities that has the same head, e.g. Coffee County and Fulton County

How can we match the coreference clusters to each one? - Use the coref_cluster spans instead of the coref_head_clusters.
"""


"""
Split get descriptors into two methods one for, compound dependencies of the head and another for chunk descriptors

Create associated entity method on doc resolve

filter the descriptors to add only PROPN, NOUN (if PROPN then check for asociated entities) and ADJ if token head is the the original head of coref

1. Check for new potential heads to add to descriptors,
2.
- Check the cluster spans for adjectives that describe the head
- Check for other entities that are associated to the head
    - Get the head of the span (we can use coref_cluster_heads, check for other PROPN/NOUNs that are not the entity in question and that have the head of the cluster as the token.head)
    - Optional check if the entity is one of the detected ones already (if this is the case the method must be in the DocResolve class and not the Entity class)
- Remove capitals for personal Nouns

"""


# Download article
url_1 = 'https://edition.cnn.com/2023/08/13/politics/coffee-county-georgia-voting-system-breach-trump/index.html'
text_1 = NewsPlease.from_url(url_1).maintext

# Apply NLP
doc = nlp(text_1)

mydoc = DocResolve(doc, top_x = 5)

"""
for index_token, token in enumerate(mydoc.doc):
    for ent in mydoc.entities:
        for coref in ent.coref_spans:
            if coref.end > index_token:
                break
            if (index_token >= coref.start) and (index_token <= coref.end) and (coref and token._.blob.polarity):
                print(f"{ent.name:<25}: {token.text:<15} polarity: {token._.blob.polarity:>6},\t subjectivity: {token._.blob.subjectivity:>6},\t start : {index_token}, \t pos: {token.pos_}, \t dep: {token.dep_}")


        
"""

print()
for ent in mydoc.entities:
    print(ent.head, ":\n descriptors: ", ent.descriptors,
          "\n related ents: ", ent.related_entities,
          "\n chunk descriptor: ", ent.chunk_descriptors,
          "\n adjectives: ", ent.adjectives)
    print()

# 'nsubj', 'dobj', 'pobj'

print()
for ent in mydoc.entities:
    print(ent.head, ": ", ent.kb_id)
    pprint(ent.kb_candidates)
    print()
"""
for i, token in enumerate(doc):
    if token._.blob.polarity:
        print(f"{token.text:<15} polarity: {token._.blob.polarity:>6},\t subjectivity: {token._.blob.subjectivity:>6},\t start : {i}, \t pos: {token.pos_}, \t dep: {token.dep_}")

"""


"""
for assessment in mydoc.doc._.blob.sentiment_assessments.assessments:
    for word in assessment[0]:
        print(word.text, word.start, word.end)
"""



# 'nsubj', 'dobj', 'pobj'





"""
# Download article
url_2 = 'https://www.foxnews.com/politics/trump-indicted-georgia-probe-alleged-efforts-overturn-2020-election'
text_2 = NewsPlease.from_url(url_2).maintext

# Apply NLP
doc_2 = nlp(text_2)
foxdoc = DocResolve(doc_2, top_x = 5)


print()
for ent in foxdoc.entities:
    print(ent.head, ":\n descriptors: ", ent.descriptors,
          "\n related ents: ", ent.related_entities,
          "\n chunk descriptor: ", ent.chunk_descriptors,
          "\n adjectives: ", ent.adjectives)
    print()


print()
for ent in foxdoc.entities:
    print(ent.head, ": ", ent.kb_id)
    pprint(ent.kb_candidates)
    print()

print(foxdoc.doc._.blob.polarity)
print(foxdoc.doc._.blob.subjectivity)
print(foxdoc.doc._.blob.sentiment_assessments.assessments)
"""


"""
for item in ent.coref_clusters:
    print([(token.text, token.pos_, token.dep_, token.head.text) for token in item])
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
