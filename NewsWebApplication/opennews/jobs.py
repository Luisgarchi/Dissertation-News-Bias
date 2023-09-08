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


ARTICLE_SIMILARITY_THRESHOLD = 0.25
SCHEDULE_TIME = '31'


gn =  GoogleNews(lang = 'en')
gn_top = gn.top_news()['entries']


@scheduler.task(id = 'getnews', trigger = 'cron', minute = SCHEDULE_TIME)
def getnews():

    with app.app_context():


        for gn_article in gn_top:
            url = url_google_to_original(gn_article["link"])
            print("Found url: ", url)
            
            # Check whether article has already been saved
            article = Article.query.filter_by(url = url).first()
            if validators.url(url) and not article:
                process_article(url, gn_article)


            article = Article.query.filter_by(url = url).first()
            if article:
                find_related_articles(article)

    
    print("updated")





def process_article(url, gn_article):
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
            save_article(tidy_article, url, publisher)




def parse_gn_query(items):
    return '+'.join(items)



def find_related_articles(article):

    publisher_ids_already_article = [id[0] for id in db.session.query(Article.publisher_id.distinct()).filter_by(event_id = article.event_id).all()]
    other_publishers = [name[0] for name in db.session.query(Publisher.name).filter(Publisher.id.notin_(publisher_ids_already_article)).all()]
    entity_ids = [id[0] for id in db.session.query(article_entity.c.entity_id).filter(article_entity.c.article_id == article.id, article_entity.c.top == True).all()]
    top_ents_names = [name[0] for name in db.session.query(Entity.name).filter(Entity.id.in_(entity_ids)).all()]

    parse_ents = parse_gn_query(top_ents_names)

    for publisher in other_publishers:
        query = parse_gn_query([publisher, parse_ents])
        gn_search = gn.search(query = query)['entries']
        gn_article = gn_search[0]
        url = url_google_to_original(gn_article['link'])
        new_article = Article.query.filter_by(url = url).first()
        if validators.url(url) and not new_article: 
            process_article(url, gn_article)
        






def save_article(tidy_article, url, publisher):
    tidy_article['publisher_id'] = publisher.id

    # Perform nlp on article maintext
    if tidy_article["maintext"]:
        
        article_nlp_obj = DocResolve(tidy_article["maintext"])
        tidy_article['polarity'] = article_nlp_obj.get_doc_polarity()
        tidy_article['subjectivity'] = article_nlp_obj.get_doc_subjectivity()
        tidy_article['lead'] = article_nlp_obj.lead

        # Find the event that this article is associated with
        date_delta = np.timedelta64(1, 'D')
        date_1 =  (tidy_article['published_date'] - date_delta).astype(datetime)
        date_2 =  (tidy_article['published_date'] + date_delta).astype(datetime)

        tidy_article['published_date'] = tidy_article['published_date'].astype(datetime)


        similar_articles = Article.query.filter(Article.published_date.between(date_1, date_2)).all()
        print(similar_articles)
        for article in similar_articles:
            print(compute_cosine_CV(article.lead, tidy_article['lead'], tokenized = False))
    
        similar_articles =  [article for article in similar_articles if compute_cosine_CV([article.title, article.lead], [tidy_article['title'], tidy_article['lead']], tokenized = False) >= ARTICLE_SIMILARITY_THRESHOLD]
        print(similar_articles)
        similar_articles = sorted(similar_articles, reverse = True, key=lambda article: compute_cosine_CV([article.title, article.lead], [tidy_article['title'], tidy_article['lead']], tokenized = False))
        print(similar_articles)

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
            
            if Article.query.filter_by(id=article_id).first() and Entity.query.filter_by(kb_id = ent['kb_id']).first():
                try:
                    statement = article_entity.insert().values(**ent_art_params) 
                    db.session.execute(statement)
                    db.session.commit()
                except:
                    continue