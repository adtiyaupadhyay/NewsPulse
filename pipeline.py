"""
pipeline.py
------------
The orchestrator. This is the file you actually run.

What it does, in plain English:
  1. Look at config.py to see which sources to scrape.
  2. For each source, spin up the right scraper (static or selenium).
  3. Get back a list of articles.
  4. Try to insert each one into the database.
  5. Print a summary: how many new articles, how many were duplicates.

This is also where you'd log failures — if source scraping crashes,
we don't want the WHOLE pipeline to die; we want to log it and move
on to the next source. That's the "maintain quality and accuracy at
high volume" line from the JD, in code form.
"""

from config import SOURCES
from database import init_db, insert_article
from scrapers.static_scraper import StaticScraper
# from scrapers.selenium_scraper import SeleniumScraper  # Phase 2


def get_scraper_for_source(source_config: dict):
    """Picks the right scraper class based on the 'type' field in config.py.
    This is the ONLY place that needs to know both scraper types exist."""
    if source_config["type"] == "static":
        return StaticScraper(source_config)
    elif source_config["type"] == "selenium":
        raise NotImplementedError("Selenium scraper is Phase 2 — coming next.")
    else:
        raise ValueError(f"Unknown source type: {source_config['type']}")


def run_pipeline():
    init_db()  # safe to call every time — it only creates the table if missing

    total_new = 0
    total_duplicate = 0
    total_failed_sources = 0

    for source_config in SOURCES:
        source_name = source_config["name"]
        print(f"\nScraping: {source_name} ...")

        try:
            scraper = get_scraper_for_source(source_config)
            articles = scraper.scrape()
        except Exception as e:
            # We log and continue rather than crashing the whole run.
            print(f"  ⚠️  FAILED to scrape {source_name}: {e}")
            total_failed_sources += 1
            continue

        print(f"  Found {len(articles)} articles on the page.")

        new_count = 0
        dup_count = 0
        for article in articles:
            was_inserted = insert_article(
                source=article["source"],
                title=article["title"],
                url=article["url"],
            )
            if was_inserted:
                new_count += 1
            else:
                dup_count += 1

        print(f"  -> {new_count} new, {dup_count} already in database.")
        total_new += new_count
        total_duplicate += dup_count

    print("\n" + "=" * 40)
    print(f"Pipeline run complete.")
    print(f"  New articles stored : {total_new}")
    print(f"  Duplicates skipped  : {total_duplicate}")
    print(f"  Sources failed      : {total_failed_sources}")
    print("=" * 40)


if __name__ == "__main__":
    run_pipeline()
