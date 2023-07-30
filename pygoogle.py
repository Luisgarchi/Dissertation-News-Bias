from pygooglenews import GoogleNews
import json
import time

gn = GoogleNews(lang = 'en', country = 'UK')

July23 = gn.search(query = 'spain+election', from_ = '2023-07-23', to_ = '2023-07-25')

entries = July23["entries"]

print(entries[0].keys())

count = 0
for entry in entries:
    count = count + 1
    print(str(count) + ". " + entry["title"] + ", " + entry["published"])
    print(entry["link"])
    time.sleep(0.25)


"""
top = gn.top_news()

entries = top["entries"]
count = 0

for entry in entries:
   count = count + 1
   # print(str(count) + ". " + entry["title"] + entry["published"])
   time.sleep(0.25)

   
"""