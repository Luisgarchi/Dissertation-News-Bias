import newspaper

paper = newspaper.build('http://www.bbc.co.uk/')

for article in paper.articles:
    print(article.url)