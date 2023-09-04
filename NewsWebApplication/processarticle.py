import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
from newsplease import NewsPlease
from pprint import pprint
from collections import Counter
from nlptools import unique_maintain_order, remove_punctuation, tokenize_number_words
import re


"""__________SPACY PIPELINE__________"""


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

#print(nlp.pipe_names)





"""__________ENTITY CLASS__________"""


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
        self.spans = []
        self.sentiment_words = []
        self.polarity_list= []
        self.subjectivity_list = []
        self.polarity = 0
        self.subjectivity = 0


    def add_knowledge_base_info(self, kb_candidates_info):
        self.kb_candidates = kb_candidates_info

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

                tokenized_words = tokenize_number_words(remove_punctuation(first_sentence), 50)
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

    def add_spans(self, spans):
        self.spans = spans

    def add_sentiment(self, token, polarity, subjectivity):
        self.sentiment_words.append(token)
        self.polarity_list.append(polarity)
        self.subjectivity_list.append(subjectivity)

    def calculate_sentiment(self):
        polarity = sum(self.polarity_list)/len(self.polarity_list) if len(self.polarity_list) != 0 else 0
        self.polarity = round(polarity, 2)
        subjectivity = sum(self.subjectivity_list)/len(self.subjectivity_list) if len(self.subjectivity_list) != 0 else 0
        self.subjectivity = round(subjectivity, 2)

    def __repr__(self):
        return f"{self.name}, {self.type}, {self.count}"
        




"""__________CREATE DOCRESOLVER CLASS__________"""


class DocResolve:

    def __init__(self, text):
        self.doc = nlp(text)
        self.ranked_entities = self.ranked_entities()
        self.entities = self.merge_entities(self.ranked_entities)
        
        self.NED_preprocess()
        self.apply_sentiment_analysis()
        
        self.lead = " ".join(tokenize_number_words(remove_punctuation(text), 50))



    def ranked_entities(self):
        entities = [(ent.text, ent.label_) for ent in self.doc.ents]    # ent._.kb_qid
        ent_count = Counter(entities).most_common()

        entities = []
        for ent in ent_count:
            entities.append(Entity(ent[0][0], ent[0][1], ent[1]))

        return entities


    def merge_entities(self, entities):

        entities_most_common = entities.copy()

        """Establish helper function"""
        def perform_pass_entity_check(ent):
            j = 0

            while entities_most_common and j < len(entities_most_common):
                ent_B = entities_most_common[j]
                if ((ent.type == ent_B.type) and
                    (ent.name.lower() in ent_B.name.lower() or ent_B.name.lower() in ent.name.lower())):

                    candidates.append(ent_B)
                    entities_most_common.pop(j)
                    continue
                
                j += 1


        """Return the top_x entities, check for subsets of the same entity"""

        entities = []
        i = 0
        while entities_most_common:

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

        for ent in self.doc.ents:
            if (ent.text.lower() in entity.name.lower()) or (entity.name.lower() in ent.text.lower()):
                if ent._.kb_qid:      
                    if ent._.kb_qid not in kb_candidates:
                        kb_candidates[ent._.kb_qid] = {}
                        kb_candidates[ent._.kb_qid]['count'] = 1
                        kb_candidates[ent._.kb_qid]['description'] = ent._.description
                        kb_candidates[ent._.kb_qid]['instance'] = get_instance(ent._.other_ids)
                    else:
                        kb_candidates[ent._.kb_qid]['count'] += 1
        
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
            # vote is cast if the head of an entity appears in the coreference cluster head
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
    

        # Final step is to merge the coreference spans with the orignial entitys found by the NER model.
        for entity in self.entities:
            spans_ner = [self.doc[ent.start:ent.end] for ent in entity.ent_obj]
            spans_coref = [span for span in entity.coref_spans]
            spans = spans_ner + spans_coref
            spans = spacy.util.filter_spans(spans)
            entity.add_spans(spans)
    
    
    

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
            self.get_ner_descriptors(entity)
        
        self.get_coref_clusters()

        for entity in self.entities:
            entity.resolve_kb_candidates()
        

    def apply_sentiment_analysis(self):

        for token in self.doc: 
            if token._.blob.polarity:
                found = False
                for ent in self.entities:
                    for span in ent.spans:
                    # Adjective tokens 
                        if token.pos_ in ['ADJ', 'ADV', 'NOUN']:

                            # First check if the head is an entity
                            if ((token.head.i >= span.start and token.head.i <= span.end)
                                or (span.root.i in [t.i for t in token.head.children if t.i != token.i])):
                                ent.add_sentiment(token.text, token._.blob.polarity, token._.blob.subjectivity)
                                found = True

                            # Second navigate the parse tree and find the 
                            # Disambiguate between more than one entity

                        elif token.pos_ == 'VERB':
                            if ((token.dep_ == 'ROOT' and span.root.i in [t.text for t in token.children])
                                or (token.dep_ == 'relcl' and span.root.i in [t.i for t in token.head.head.children])):
                                ent.add_sentiment(token.text, token._.blob.polarity, token._.blob.subjectivity)
                                found = True

                        elif (token.i >= span.start and token.i <= span.end):
                            ent.add_sentiment(token.text, token._.blob.polarity, token._.blob.subjectivity)
                            found = True

                if not found:
                    nearest_ent = None
                    distance = float('inf')
                    for ent in self.entities:
                        for span in ent.spans:

                            from_start = abs(token.i - span.start)
                            from_end = abs(token.i -span.end)

                            closest = from_start if from_start < from_end else from_end

                            if closest < distance:
                                distance = closest
                                nearest_ent = ent
                    
                    if nearest_ent:
                        nearest_ent.add_sentiment(token.text, token._.blob.polarity, token._.blob.subjectivity)

        for ent in self.entities:
            ent.calculate_sentiment()


    def top_entities(self):

        # Return a dictionary with the top 3 most mentioned entities.
        # Also get the top 

        relvant_ents = [ent for ent in self.entities if ent.type in ['PERSON', 'GPE', 'ORG'] and ent.count >= 2]

        top = sorted(relvant_ents, key=lambda entity: entity.count, reverse = True)[:3]
        top = [{'name':ent.name, 'count':ent.count, 'kb_id':ent.kb_id, 'polarity': ent.polarity, 'top': True} for ent in top]

        top_name = [entity['name'] for entity in top]

        biased = sorted(relvant_ents, key=lambda entity: entity.polarity, reverse = True)
        biased = [{'name':ent.name, 'count':ent.count, 'kb_id':ent.kb_id, 'polarity': ent.polarity, 'top': False} for ent in biased if ent.name not in top_name][-3:3]

        return top + biased

    def get_doc_polarity(self):
        return round(self.doc._.blob.polarity, 2)

    def get_doc_subjectivity(self):
        return round(self.doc._.blob.subjectivity, 2)
    

        

                    
 

    



"""
Bug ticket - for DocResolve.get_coref_clusters()
What if there are two or more entities that has the same head, e.g. Coffee County and Fulton County
How can we match the coreference clusters to each one? - Use the coref_cluster spans instead of the coref_head_clusters.
"""

"""
Split get descriptors into two methods one for, compound dependencies of the head and another for chunk descriptors


1. Check for new potential heads to add to descriptors,
2.
- Check the cluster spans for adjectives that describe the head
- Check for other entities that are associated to the head
    - Get the head of the span (we can use coref_cluster_heads, check for other PROPN/NOUNs that are not the entity in question and that have the head of the cluster as the token.head)
    - Optional check if the entity is one of the detected ones already (if this is the case the method must be in the DocResolve class and not the Entity class)
- Remove capitals for personal Nouns

"""
"""

# Download article
url_1 = 'https://edition.cnn.com/2023/08/13/politics/coffee-county-georgia-voting-system-breach-trump/index.html'
text_1 = NewsPlease.from_url(url_1).maintext

# Apply NLP
doc = nlp(text_1)

url_2 = 'https://www.foxnews.com/politics/trump-indicted-georgia-probe-alleged-efforts-overturn-2020-election'


# Download article
url_1 = 'https://edition.cnn.com/2023/08/13/politics/coffee-county-georgia-voting-system-breach-trump/index.html'
text_1 = NewsPlease.from_url(url_1).maintext

# Apply NLP
doc = nlp(text_1)



mydoc = DocResolve(text_1)
mydoc.top_entities()


"""
"""
for ent in mydoc.entities:
    if ent.count > 1:
        print(ent.name, ":\n descriptors: ", ent.descriptors,
            "\n type: ", ent.type,
            "\n count: ", ent.count,
            "\n wikidata id: ", ent.kb_id,
            "\n coreferences: ", ent.spans,
            "\n polarity: ", ent.polarity,
            "\n subjectivity ", ent.subjectivity,
            "\n related ents: ", ent.related_entities,
            "\n chunk descriptor: ", ent.chunk_descriptors,
            "\n adjectives: ", ent.adjectives)
        print()
"""

