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
                del entities_most_common[j]
                continue
            
            j += 1


    """Return the top_x entities, check for subsets of the same entity"""

    entities = []
    i = 0
    while entities_most_common and i < top_x:

        # Get the top entity
        ent_A = entities_most_common[0]
        del entities_most_common[0]

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

candidate_disambiguation = {}
ranked_entities_list = [ent[0][0] for ent in top_entities(ranked_entities, 5)]

for found_entity in ranked_entities_list:
    entities = [(ent._.kb_qid, ent._.description) for ent in doc.ents if ent.text == found_entity]
    candidate_disambiguation[found_entity] = set(entities)

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


