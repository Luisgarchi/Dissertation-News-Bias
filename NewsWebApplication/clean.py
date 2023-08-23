import spacy
from spacy import displacy
from newsplease import NewsPlease
from pprint import pprint
from collections import Counter
import re
import copy

# Create pipeline
nlp = spacy.load("en_core_web_trf")
nlp.add_pipe('entityfishing', config={"extra_info": True})

print(nlp.pipe_names)

# Download article
url_1 = 'https://edition.cnn.com/2023/08/13/politics/coffee-county-georgia-voting-system-breach-trump/index.html'
text_1 = NewsPlease.from_url(url_1).maintext

# Apply NLP
doc = nlp(text_1)



# Get the top X = 5 Entities
entities = [(ent.text, ent.label_) for ent in doc.ents]    # ent._.kb_qid
ranked_entities = Counter(entities).most_common()
pprint(ranked_entities)


def top_entities(ranked_entities, top_x):

    entities_most_common = copy.deepcopy(ranked_entities)

    """Establish helper function"""
    def perform_pass_entity_check():
        j = 0
        while entities_most_common and j < len(entities_most_common):
            ent_B = entities_most_common[j]
            if ent_A[0][1] == ent_B[0][1] and (ent_A[0][0] in ent_B[0][0] or ent_B[0][0] in ent_A[0][0]):
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
        perform_pass_entity_check()

        # perform a second pass check over the list with any candidates found in the previous step
        k = 0
        while candidates and k < len(candidates):
            ent_C = candidates[k]
            perform_pass_entity_check()
            k += 1
        
        # Second to last step merge all the candidates with initial candidate (ent_A)
        count = ent_A[1]
        for candidate in candidates:
            count += candidate[1]

        # Save the merged canidate entity
        entities.append((ent_A[0], count))

        # Last step increase the counter by 1
        i += 1
    
    return entities

pprint(top_entities(ranked_entities, 5))





class BasicEntity:
    def __init__(self, name, type, count):
        self.name  = name
        self.type  = type
        self.count = count

    def add_count(self, count):
        self.count += count



class Entity(BasicEntity):
    def __init__(self, ent_info, kb_candidates_info):
        self.name = ent_info.name
        self.type = ent_info.type
        self.count = ent_info.count
        self.kb_candidates = kb_candidates_info
        self.ent_obj = None
        






class DocResolve:

    def __init__(self, doc, top_x = 5):
        self.doc = doc
        self.ranked_entities = self.ranked_entities(self.doc)
        self.merge_entities = self.merge_entities(self.ranked_entities, top_x)



    def ranked_entities(self, doc):
        entities = [(ent.text, ent.label_) for ent in doc.ents]    # ent._.kb_qid
        ent_count = Counter(entities).most_common()

        entities = []
        for ent in ent_count:
            entities.append(BasicEntity(ent[0][0], ent[0][1], ent[1]))

        return entities



    def merge_entities(self, entities, top_x):

        entities_most_common = entities.copy()

        """Establish helper function"""
        def perform_pass_entity_check(ent):
            j = 0
            while entities_most_common and j < len(entities_most_common):
                ent_B = entities_most_common[j]
                if ent.type == ent_B.type and (ent.name in ent.name or ent.name in ent.name):
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
            count = ent_A.count
            for candidate in candidates:
                count += candidate.count

            # Save the merged canidate entity

            entities.append(BasicEntity(ent_A.name, ent_A.type, count))

            # Last step increase the counter by 1
            i += 1
        
        return entities
    

"""
    def NED_preprocess(self):
        
        for ent_info in self.merge_entities:

        ranked_entities_list = [ent[0] for ent in self.merge_entities]
        
        for found_entity in ranked_entities_list:
            count = Counter([(ent._.kb_qid, ent._.description) for ent in doc.ents if (ent.text in ent_info[0]) or (ent_info[0] in ent.text)]).most_common()
            unpack_count = [(candidate[0][0], candidate[0][1], candidate[1]) for candidate in count]

"""









candidate_disambiguation = {}
ranked_entities_list = [ent[0][0] for ent in top_entities(ranked_entities, 5)]


for found_entity in ranked_entities_list:

    entities_data = []
    entities_span =[]

    count = Counter([ent._.kb_qid for ent in doc.ents if (ent.text in found_entity) or (found_entity in ent.text)]).most_common()
    description = {}
    
    for ent in doc.ents:

        if ent._.kb_qid in count and ent._.kb_qid not in description:
            description[ent._.kb_qid] = ent._.description
        
        """ FOBFO KMFPKM KPFDM FP"""


        if (ent.text in found_entity) or (found_entity in ent.text):
            entities_span = []

            if ent._.kb_qid in entities_data:
                continue
            entities_data.extend([ent._.kb_qid, ent._.description])
    
    entities_data.append(count)
    candidate_disambiguation[found_entity] = entities_data


pprint(candidate_disambiguation)




def is_candidate(cluster_tokens):
    for token in cluster_tokens:
        if token in top_entities:
            return True
    return False


"""
def matching_coreference_clusters(top_entities, clusters):

    def is_candidate(cluster_tokens):
        for token in cluster_tokens:
            if token in top_entities:
                return True
        return False
    

    candidate_coref = {key : val for key, val in clusters if re.match(r"coref_clusters_*", key) and is_candidate(val, top_entities)}


    matching_clusters = {}

    for entity in top_entities: 

"""




#pprint([(ent.text, ent.label_, ent._.kb_qid) for ent in doc.ents if 'Giuliani' in ent.text ])


