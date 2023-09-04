from opennews import scheduler
from pygooglenews import GoogleNews
from nlptools import url_google_to_original, filter_newsplease_attributes, compute_cosine_CV
import validators
import numpy as np
from newsplease import NewsPlease
from opennews.models import Article, Publisher, Entity, Event, article_entity
from opennews import app, db
from processarticle import DocResolve
from datetime import datetime


ARTICLE_SIMILARITY_THRESHOLD = 0.3
SCHEDULE_TIME = '51'



@scheduler.task(id = 'getnews', trigger = 'cron', minute = SCHEDULE_TIME)
def getnews():

    gn =  GoogleNews(lang = 'en')
    gn_news = gn.top_news()['entries']

    with app.app_context():


        for gn_article in gn_news:
            url = url_google_to_original(gn_article["link"])
            print("Found this url: ", url)
            
            # Check whether article has already been saved
            article_id = Article.query.filter_by(url = url).first()
            
            # Check if valid url
            if validators.url(url) and not article_id:
                print("New Article found")
                np_article = NewsPlease.from_url(url)
                
                # Verify sucessful extraction
                if np_article:
                    tidy_article = filter_newsplease_attributes(np_article, gn_article.title)
                    
                    # Get the correct publisher id
                    publisher_name = tidy_article.pop('publisher')
                    publisher = Publisher.query.filter_by(name = publisher_name).first()
                    
                    # Only add article if it is a publisher in the database
                    if publisher:

                        print("Found: publisher in DB: ", publisher.name)

                        tidy_article['publisher_id'] = publisher.id

                        # Perform nlp on article maintext
                        article_nlp_obj = DocResolve(tidy_article["maintext"])
                        tidy_article['polarity'] = article_nlp_obj.get_doc_polarity()
                        tidy_article['subjectivity'] = article_nlp_obj.get_doc_subjectivity()
                        tidy_article['lead'] = article_nlp_obj.lead

                        # Find the event that this article is associated with
                        date_delta = np.timedelta64(1, 'D')
                        date_1 =  (tidy_article['published_date'] - date_delta).astype(datetime)
                        date_2 =  (tidy_article['published_date'] + date_delta).astype(datetime)

                        tidy_article['published_date'] = tidy_article['published_date'].astype(datetime)


                        similar_articles = Article.query.filter(Article.published_date.between(date_1, date_2))
                        similar_articles = filter(lambda article: compute_cosine_CV(article.lead, tidy_article['lead'], tokenized = True) >= ARTICLE_SIMILARITY_THRESHOLD, similar_articles)

                        similar_articles = sorted(similar_articles, key=lambda article: compute_cosine_CV(article.lead, tidy_article['lead'], tokenized = True))
                        

                        if similar_articles:
                            tidy_article['event_id'] = similar_articles[0].event_id
                            print("Event found for article")
                        # If there is no previous event create a new one
                        else:
                            print("Article does not have Event, adding event")
                            db.session.add(Event(date = tidy_article['published_date'], first_url = url))
                            db.session.commit()
                            tidy_article['event_id'] = Event.query.filter_by(first_url = url).first().id
                        
                        
                        db.session.add(Article(**tidy_article))
                        db.session.commit()
                        # ADD HTML

                        entities = article_nlp_obj.top_entities()               # Retrieve the entities
                        article_id = Article.query.filter_by(url = url).first().id


                        # Add Entities to Entity model and article_entity table
                        for ent in entities:

                            ent_id = Entity.query.filter_by(kb_id = ent['kb_id']).first()
                            if not ent_id:
                                print("New Entity found: ", ent["name"])
                                ent_params = {key: ent[key] for key in ['name', 'kb_id']}
                                db.session.add(Entity(**ent_params))
                                db.session.commit()                                     # need to commit to ensure new entity id's are in the DB
                                ent_id = Entity.query.filter_by(kb_id = ent['kb_id']).first().id
                            else:
                                ent_id = ent_id.id

                            # Add to the article_entity database
                            ent['entity_id']  = ent_id
                            ent['article_id'] = article_id
                            ent_art_params = {key: ent[key] for key in ['article_id', 'entity_id', 'polarity', 'count', 'top']}

                            statement = article_entity.insert().values(**ent_art_params) 
                            db.session.execute(statement)
                            db.session.commit()
    
    print("updated")
