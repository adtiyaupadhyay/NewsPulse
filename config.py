"""
config.py
---------
This is the ONE file you edit to add/remove sources.
No scraping logic lives here — just WHERE to look and WHAT to grab.
"""

SOURCES = [
    {
        "name": "Hacker News",
        "url": "https://news.ycombinator.com/",
        "type": "static",
        "selectors": {
            "article_row": "tr.athing",
            "title": "span.titleline > a",
            "link_attr": "href",
        },
    },
    {
        # Included specifically to DEMONSTRATE Selenium, not as a real
        # news feed. Its content only exists after JavaScript runs —
        # confirmed by checking its raw page source, which is empty
        # until JS builds it. It's a well-known scraping practice site
        # (built by Scrapinghub, the makers of Scrapy) made exactly for
        # this purpose. Framing it honestly ("I added this to prove I
        # know WHEN Selenium is needed, not just that I can use it")
        # is a stronger interview answer than mislabeling it as news.
        "name": "Quotes (JS-rendered demo)",
        "url": "https://quotes.toscrape.com/js/",
        "type": "selenium",
        "selectors": {
            "article_row": "div.quote",
            "title": "span.text",
        },
    },
]

DATABASE_PATH = "newspulse.db"