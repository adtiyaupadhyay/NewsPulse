"""
config.py
---------
This is the ONE file you edit to add/remove news sources.
No scraping logic lives here — just WHERE to look and WHAT to grab.

Why this matters (interview point): if the scraper logic and the
source-specific details were mixed together, adding a new site would
mean copy-pasting a whole new scraper function. Instead, adding a
source is just adding a dictionary entry below.
"""

SOURCES = [
    {
        "name": "Hacker News",
        "url": "https://news.ycombinator.com/",
        "type": "static",          # static = requests+BeautifulSoup is enough
        "selectors": {
            "article_row": "tr.athing",   # each story sits in a <tr class="athing">
            "title": "span.titleline > a",
            "link_attr": "href",
        },
    },
    # Example of how you'd add a JS-heavy source later (Phase 2):
    # {
    #     "name": "SomeJSHeavySite",
    #     "url": "https://example.com/news",
    #     "type": "selenium",       # selenium = page needs JS to render content
    #     "selectors": {
    #         "article_row": "div.story-card",
    #         "title": "h2.story-title",
    #         "link_attr": "href",
    #     },
    # },
]

DATABASE_PATH = "newspulse.db"
