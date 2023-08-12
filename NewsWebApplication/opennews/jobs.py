from opennews import scheduler
from pygooglenews import GoogleNews
from nlptools import url_google_to_original, filter_newsplease_attributes
import validators
from newsplease import NewsPlease
from opennews.models import Article
from opennews import app, db



SCHEDULE_TIME = '3,20,55'



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
                article = NewsPlease.from_url(url)
                
                # Verify sucessful extraction and add to db
                if article:
                    tidy_article = filter_newsplease_attributes(article)

                    db.session.add(Article(**tidy_article))
                    db.session.commit()
    
    print("updated")




