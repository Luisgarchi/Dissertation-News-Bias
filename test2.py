from pygooglenews import GoogleNews


gn =  GoogleNews(lang = 'en')
gn_news = gn.top_news()['entries']



count = 0
for entry in gn_news:
    count = count + 1
    print(str(count) + ". " + entry["title"] + ", " + entry["published"])
    print(entry["link"])