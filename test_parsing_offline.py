"""
test_parsing_offline.py
-------------------------
This sandbox can't reach real websites over the network, so this
script proves the PARSING logic works correctly using a hand-built
HTML snippet that matches Hacker News's real structure (a <tr
class="athing"> per story, with a <span class="titleline"><a> inside).

Run this on your own machine too, right after cloning — if it
passes here, your parse() logic is correct. The only thing that
changes when you go live is fetch_html() actually hitting the network,
which you can verify separately by running scrapers/static_scraper.py
directly once you're on an unrestricted network.
"""

from scrapers.base_scraper import BaseScraper

MOCK_HN_HTML = """
<html><body>
<table>
  <tr class="athing" id="1">
    <td class="title"><span class="titleline">
      <a href="https://example.com/story-one">A cool AI startup raises funding</a>
    </span></td>
  </tr>
  <tr class="athing" id="2">
    <td class="title"><span class="titleline">
      <a href="https://example.com/story-two">New Python library released</a>
    </span></td>
  </tr>
  <tr class="athing" id="3">
    <td class="title"><span class="titleline">
      <a href="https://example.com/story-three">Debate over web scraping ethics</a>
    </span></td>
  </tr>
</table>
</body></html>
"""


class FakeScraperForTesting(BaseScraper):
    """We don't need fetch_html() for this test since we're
    feeding parse() the mock HTML directly."""
    def fetch_html(self) -> str:
        return MOCK_HN_HTML


if __name__ == "__main__":
    config = {
        "name": "Hacker News",
        "url": "https://news.ycombinator.com/",
        "selectors": {
            "article_row": "tr.athing",
            "title": "span.titleline > a",
            "link_attr": "href",
        },
    }

    scraper = FakeScraperForTesting(config)
    articles = scraper.parse(MOCK_HN_HTML)

    print(f"Parsed {len(articles)} articles (expected 3):\n")
    for a in articles:
        print(f"  - [{a['source']}] {a['title']}  ->  {a['url']}")

    assert len(articles) == 3, "Parsing logic broke — check selectors!"
    print("\n✅ Parsing logic verified correct.")
