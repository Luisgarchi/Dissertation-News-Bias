from opennews import scheduler
from pygooglenews import GoogleNews
from nlptools import url_google_to_original, filter_newsplease_attributes
import validators
from newsplease import NewsPlease
from opennews.models import Article, Publisher
from opennews import app, db



SCHEDULE_TIME = '13'



@scheduler.task(id = 'getnews', trigger = 'cron', minute = SCHEDULE_TIME)
def getnews():

    gn =  GoogleNews(lang = 'en')
    gn_news = gn.top_news()['entries']

    with app.app_context():

        for gn_article in gn_news:
            url = url_google_to_original(gn_article["link"])
            
            # Check whether article has already been saved
            in_db = Article.query.filter_by(url = url).first()

            # Check if valid url
            if validators.url(url) and not in_db:
                np_article = NewsPlease.from_url(url)
                
                # Verify sucessful extraction and add to db
                if np_article:
                    tidy_article = filter_newsplease_attributes(np_article, gn_article.title)
                    
                    # Get the correct publisher id
                    publisher_name = tidy_article.pop('publisher')
                    publisher = Publisher.query.filter_by(name = publisher_name).first()

                    if publisher:
                        tidy_article['publisher_id'] = publisher.id
                    else:
                        print(publisher_name, "not in db")
                        continue

                        #DECIDE WHAT TO DO HERE
                            #OPTION 1 ADD TO DB
                            #OPTION 2 JUST SKIP
                        


                    article_nlp_obj = nlp_process()

                    # Add to db
                    db.session.add(article)
                    db.session.commit()
                    print(publisher_name, " added")
    
    print("updated")





import spacy
from pprint import pprint
from spacy import displacy
from collections import Counter


class opennews_article:

    def __init__(self, args):
        self.args = args
        self.doc  = self.nlp_process()
        self.tags = self.get_tags()



    
    def nlp_process(self):
        
        # Initialise NLP pipeline

        nlp = spacy.load("en_core_web_trf")
        nlp_coref = spacy.load("en_coreference_web_trf")

        # use replace_listeners for the coref components
        nlp_coref.replace_listeners("transformer", "coref", ["model.tok2vec"])
        nlp_coref.replace_listeners("transformer", "span_resolver", ["model.tok2vec"])

        # we won't copy over the span cleaner
        nlp.add_pipe("coref", source=nlp_coref)
        nlp.add_pipe("span_resolver", source=nlp_coref)

        return nlp(self.args.maintext)


    def get_tags(self):

        valid_tags = ['PERSON', 'NORP', 'ORGS', 'GPE', 'EVENT']
        tags = [(x.text, x.label_) for x in doc.ents if x.label_ in valid_tags]

        # get top 3
        top_tags = Counter(tags).most_common(3)

        # unpack 
        return [(name_tag[0], name_tag[1], count) for name_tag, count in top_tags]


    def get_coreference_spans(self):

        coref_len = {key : len(val) for key , val in self.doc.spans.items() if re.match(r"coref_clusters_*", key) }
        coref_keys = Counter(coref_len).most_common(3)
        coref_index = [x[0] for x in coref_keys]
        
        


        
    
        



        re.match(r"coref_clusters_*")
