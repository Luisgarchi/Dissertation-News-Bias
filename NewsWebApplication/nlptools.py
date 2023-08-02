from urllib.parse import urlsplit
import base64


def get_publisher_from_url(url):
    return urlsplit(url).netloc.split(".")[1]


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
