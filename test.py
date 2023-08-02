import base64
import validators

def url_google_to_original(url):
    # https://stackoverflow.com/questions/76082944/how-to-collect-the-url-from-the-clicked-article-instead-of-the-google-news-site
    # https://gist.github.com/perrygeo/ee7c65bb1541ff6ac770
    
    """

    str -> str

    Example: 

    https://news.google.com/rss/articles/CBMiUWh0dHBzOi8vd3d3Lm55dGltZXMuY29tLzIwMjMvMDgvMDEvdXMvcG9saXRpY3MvdHJ1bXAtcmVwdWJsaWNhbnMtcG9sbC1jcmltZXMuaHRtbNIBAA?oc=5
    
    ->
    
    https://www.nytimes.com/2023/08/01/us/politics/trump-republicans-poll-crimes.html
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

    
    
def split_non_alnum(google_url):
    i = 0
    for c in google_url:
        if not c.isalnum():
            break
        i += 1
    
    return google_url[:i]

my_urls = [
    "https://news.google.com/rss/articles/CCAiC0xiZ3RQc3NhR0UwmAEB?oc=5",
    "https://news.google.com/rss/articles/CBMiUWh0dHBzOi8vd3d3Lm55dGltZXMuY29tLzIwMjMvMDgvMDEvdXMvcG9saXRpY3MvdHJ1bXAtcmVwdWJsaWNhbnMtcG9sbC1jcmltZXMuaHRtbNIBAA?oc=5",
    "https://news.google.com/rss/articles/CBMiWWh0dHBzOi8vd3d3LmNubi5jb20vMjAyMy8wOC8wMS91cy9yZXgtaGV1ZXJtYW5uLXdpZmUtZ2lsZ28tYmVhY2gta2lsbGluZ3MtaG9tZS9pbmRleC5odG1s0gFdaHR0cHM6Ly9hbXAuY25uLmNvbS9jbm4vMjAyMy8wOC8wMS91cy9yZXgtaGV1ZXJtYW5uLXdpZmUtZ2lsZ28tYmVhY2gta2lsbGluZ3MtaG9tZS9pbmRleC5odG1s?oc=5",
    "https://news.google.com/rss/articles/CBMiX2h0dHBzOi8vd3d3LmNuYmMuY29tLzIwMjMvMDcvMzEvZGVzYW50aXMtY2xhaW1zLWJpZGVuLXdvdWxkLWJlYXQtdHJ1bXAtZ29wLXZvdGVycy1kaXNhZ3JlZS5odG1s0gFjaHR0cHM6Ly93d3cuY25iYy5jb20vYW1wLzIwMjMvMDcvMzEvZGVzYW50aXMtY2xhaW1zLWJpZGVuLXdvdWxkLWJlYXQtdHJ1bXAtZ29wLXZvdGVycy1kaXNhZ3JlZS5odG1s?oc=5",
    "https://news.google.com/rss/articles/CBMiamh0dHBzOi8vdGhlaGlsbC5jb20vaG9tZW5ld3MvaG91c2UvNDEyOTk3NC1kZXZvbi1hcmNoZXItZGViYXRlLWZvY3VzZXMtb24taHVudGVyLWJpZGVuLWlsbHVzaW9uLW9mLWFjY2Vzcy_SAW5odHRwczovL3RoZWhpbGwuY29tL2hvbWVuZXdzL2hvdXNlLzQxMjk5NzQtZGV2b24tYXJjaGVyLWRlYmF0ZS1mb2N1c2VzLW9uLWh1bnRlci1iaWRlbi1pbGx1c2lvbi1vZi1hY2Nlc3MvYW1wLw?oc=5",
    "https://news.google.com/rss/articles/CBMiSGh0dHBzOi8vd3d3Lndhc2hpbmd0b25wb3N0LmNvbS93b3JsZC8yMDIzLzA4LzAxL3J1c3NpYS11a3JhaW5lLXdhci1uZXdzL9IBAA?oc=5",
    "https://news.google.com/rss/articles/CBMiXGh0dHBzOi8vd3d3LmNic25ld3MuY29tL25ld3MvbWVtcGhpcy1wb2xpY2Utc2hvb3QtbWFuLXdoby1maXJlZC1ndW4tbWFyZ29saW4taGVicmV3LWFjYWRlbXkv0gFgaHR0cHM6Ly93d3cuY2JzbmV3cy5jb20vYW1wL25ld3MvbWVtcGhpcy1wb2xpY2Utc2hvb3QtbWFuLXdoby1maXJlZC1ndW4tbWFyZ29saW4taGVicmV3LWFjYWRlbXkv?oc=5"
]


def get_article_url2(google_url):

    # https://stackoverflow.com/questions/76082944/how-to-collect-the-url-from-the-clicked-article-instead-of-the-google-news-site

    base64_url = google_url.replace("https://news.google.com/rss/articles/","").split("?")[0]
    
    # https://gist.github.com/perrygeo/ee7c65bb1541ff6ac770

