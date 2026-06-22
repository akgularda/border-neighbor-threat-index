"""Feed mirror URL builders and headline normalization."""

from urllib.parse import quote_plus

MIRROR_QUERY_TEMPLATES = [
    "{country} news today",
    "{country} politics",
    "{country} security",
    "{country} economy",
]


def google_news_url(query):
    encoded = quote_plus(query)
    return f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"


def gdelt_url(query):
    encoded = quote_plus(query)
    return (
        f"https://api.gdeltproject.org/api/v2/doc/doc?query={encoded}"
        f"&mode=artlist&maxrecords=25&format=rss"
    )


def build_mirror_urls(country_name, include_gdelt=False):
    urls = []
    for template in MIRROR_QUERY_TEMPLATES:
        query = template.format(country=country_name)
        urls.append(google_news_url(query))
        if include_gdelt:
            urls.append(gdelt_url(query))
    return list(dict.fromkeys(urls))