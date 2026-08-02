"""
base_scraper.py
----------------
This defines the SHAPE every scraper must follow, using an abstract
base class (ABC).

Basic concept: an "abstract base class" is like a job description
with blanks. It says "every scraper MUST have a fetch_html() method
and a parse() method" — but doesn't say HOW. Each concrete scraper
(static_scraper.py, selenium_scraper.py) fills in the HOW.

Why bother with this instead of just writing separate functions?
Because your pipeline.py (the orchestrator) can then treat every
scraper identically: "call .scrape() and get back a list of
articles" — it doesn't need to know or care if that scraper used
requests or Selenium under the hood. That's the design decision
worth explaining in an interview.
"""

from abc import ABC, abstractmethod


class BaseScraper(ABC):
    def __init__(self, source_config: dict):
        self.name = source_config["name"]
        self.url = source_config["url"]
        self.selectors = source_config["selectors"]

    @abstractmethod
    def fetch_html(self) -> str:
        """Return the raw HTML of the page. Implemented differently
        by static (requests) vs Selenium scrapers."""
        raise NotImplementedError

    def parse(self, html: str) -> list[dict]:
        """Parses HTML into a list of {title, url} dicts.
        Same parsing logic works for both scraper types, since by
        the time we get here, it's just HTML text either way —
        that's the whole point of separating fetch_html() from parse()."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select(self.selectors["article_row"])

        articles = []
        for row in rows:
            title_tag = row.select_one(self.selectors["title"])
            if not title_tag:
                continue  # skip rows that don't match expected structure
            title = title_tag.get_text(strip=True)
            link = title_tag.get(self.selectors["link_attr"], "")
            if title and link:
                articles.append({
                    "source": self.name,
                    "title": title,
                    "url": link,
                })
        return articles

    def scrape(self) -> list[dict]:
        """The public method the pipeline actually calls.
        fetch -> parse -> return. Simple and predictable."""
        html = self.fetch_html()
        return self.parse(html)
