import spacy
from newsplease import NewsPlease
from spacytextblob.spacytextblob import SpacyTextBlob

text_en = "Victor Hugo and Honoré de Balzac are French writers who lived in Paris."

nlp_model_en = spacy.load("en_core_web_trf")
nlp_model_en.add_pipe("spacytextblob")


#url_1 = 'https://edition.cnn.com/2023/08/13/politics/coffee-county-georgia-voting-system-breach-trump/index.html'
#text_1 = NewsPlease.from_url(url_1).maintext

#doc_en = nlp_model_en(text_1)


text = "Atlanta-area prosecutors investigating efforts to overturn the 2020 election results in Georgia are in possession of text messages and emails directly connecting members of Donald Trump’s legal team to the early January 2021 voting system breach in Coffee County, sources tell CNN. Fulton County District Attorney Fani Willis is expected to seek charges against more than a dozen individuals when her team presents its case before a grand jury next week. Several individuals involved in the voting systems breach in Coffee County are among those who may face charges in the sprawling criminal probe. Investigators in the Georgia criminal probe have long suspected the breach was not an organic effort sprung from sympathetic Trump supporters in rural and heavily Republican Coffee County – a county Trump won by nearly 70% of the vote. They have gathered evidence indicating it was a top-down push by Trump’s team to access sensitive voting software, according to people familiar with the situation. Trump allies attempted to access voting systems after the 2020 election as part of the broader push to produce evidence that could back up the former president’s baseless claims of widespread fraud. While Trump’s January 2021 call to Georgia Secretary of State Brad Raffensperger and effort to put forward fake slates of electors have long been considered key pillars of Willis’ criminal probe, the voting system breach in Coffee County quietly emerged as an area of focus for investigators roughly one year ago. Since then, new evidence has slowly been uncovered about the role of Trump’s attorneys, the operatives they hired and how the breach, as well as others like it in other key states, factored into broader plans for overturning the election. Together, the text messages and other court documents show how Trump lawyers and a group of hired operatives sought to access Coffee County’s voting systems in the days before January 6, 2021, as the former president’s allies continued a desperate hunt for any evidence of widespread fraud they could use to delay certification of Joe Biden’s electoral victory. Last year, a former Trump official testified under oath to the House January 6 select committee that plans to access voting systems in Georgia were discussed in meetings at the White House, including during an Oval Office meeting on December 18, 2020,  that included Trump. "
doc = nlp_model_en(text)

for ent in doc.ents:
    print(doc[ent.start:ent.end])
    print(ent.root)

print()
for token in doc:
    #Adjective
    if token._.blob.polarity:
        print(token.text)

print()
for token in doc:
    #Adjective
    if token._.blob.polarity:

        #print(token.text, token.head.text)
        
        for ent in doc.ents:

            if token.pos_ == 'ADV' and token:
                print(token.text)
                if token.head.i >= ent.start and token.head.i <= ent.end:
                    #print('ADVERB - ENT = ')
                    None
                