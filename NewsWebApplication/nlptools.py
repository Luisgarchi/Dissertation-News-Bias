from urllib.parse import urlsplit
import base64
import datetime
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')


def get_pubisher_from_gn_title(title):
    return title.split('-')[-1].strip()


def url_google_to_original(url):

    # helper function for step 2
    def split_non_alnum(google_url):
        i = 0
        for c in google_url:
            if not c.isalnum():
                break
            i += 1
        
        return google_url[:i]

    # https://stackoverflow.com/questions/76082944/how-to-collect-the-url-from-the-clicked-article-instead-of-the-google-news-site
    # https://gist.github.com/perrygeo/ee7c65bb1541ff6ac770
    
    """
    str -> str
    Example: 
    Input:  'https://news.google.com/rss/articles/CBMiUWh0dHBzOi8vd3d3Lm55dGltZXMuY29tLzIwMjMvMDgvMDEvdXMvcG9saXRpY3MvdHJ1bXAtcmVwdWJsaWNhbnMtcG9sbC1jcmltZXMuaHRtbNIBAA?oc=5'
    ->
    Output: 'https://www.nytimes.com/2023/08/01/us/politics/trump-republicans-poll-crimes.html'
    """

    # Step 1 remove google and ?
    base64code = url.replace("https://news.google.com/rss/articles/","").split("?")[0]

    # Step 2 split if it does not have an alpha numeric character
    base64code = split_non_alnum(base64code)

    # Step 3 Add required padding
    pad =  len(base64code) % 4     # (4 - len(url) % 4) % 4
    base64code = f"{base64code}{'=' * pad}"

    # Step 4 Decode

    # [4:-3] removes leading and trailing bytes
    base64code = base64.b64decode(base64code)[4:-3]

    # In case trailing bytes were a second url spit in the middle and drop the second url
    if b'\xd2\x01' in base64code:
        base64code = base64code.split(b'\xd2\x01')[0]
        
    # Convert url to string
    base64code = base64code.decode('latin-1')

    return base64code

def filter_newsplease_attributes(article_obj, gn_title):

    """The dictionary keys are the same names as the attributes of the articles table in the DB.
    This is so that the dictionary can be passed as a set of arguments to the SQLAlchemy model."""

    article = {
        "title": str(article_obj.title),
        "maintext": str(article_obj.maintext),
        "published_date": article_obj.date_publish,
        "url" : str(article_obj.url),
        "publisher": get_pubisher_from_gn_title(gn_title)
    }

    return article



def unique_maintain_order(seq):
    # https://stackoverflow.com/questions/480214/how-do-i-remove-duplicates-from-a-list-while-preserving-order
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def remove_punctuation(text):
    
    # Removes punctuation (str -> str)
    
    remove_punctuation = string.punctuation + "‘’’—“”"
    return text.lower().translate(str.maketrans('', '', remove_punctuation))

# We have to remove the punctation from stop words because 
# punctuation will be remove from the text, 
# inorder for them to match they must be processed the same (or removed before)


def tokenize_number_words(text, number):
    
    # Tokenizes words, removes stop words and returns the first n number of tokens (str -> list)
    sw = [remove_punctuation(word) for word in stopwords.words('english')]
    tokenized = word_tokenize(text)
    
    i = 0
    while i < number and i < len(tokenized):
        if tokenized[i] in sw: 
            del tokenized[i]
        else: 
            i += 1
    
    if number < len(tokenized):
        del tokenized[number:]
    
    return tokenized



