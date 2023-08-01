from urllib.parse import urlsplit

def get_publisher_from_url(url):
    return urlsplit(url).netloc.split(".")[1]