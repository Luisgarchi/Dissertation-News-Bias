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



def top_entities(ranked_entities, top_x):

    """Establish helper function"""
    def perform_pass_entity_check():
        j = 0
        while ranked_entities and j < len(ranked_entities):
            ent_B = ranked_entities[j]
            if ent_A[0][1] == ent_B[0][1] and (ent_A[0][0] in ent_B[0][0] or ent_B[0][0] in ent_A[0][0]):
                candidates.append(ent_B)
                del ranked_entities[j]
                continue
            
            j += 1


    """Return the top_x entities, check for subsets of the same entity"""

    entities = []
    i = 0
    while ranked_entities and i < top_x:

        # Get the top entity
        ent_A = ranked_entities[0]
        del ranked_entities[0]

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

#pprint([(ent.text, ent.label_, ent._.kb_qid) for ent in doc.ents if 'Giuliani' in ent.text ])


