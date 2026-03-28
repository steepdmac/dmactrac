"""
Custom CLI commands for dmactrac.
"""

import json
import time
from datetime import date
from pathlib import Path

import click
import requests
from flask import current_app
from flask.cli import with_appcontext
from pyzotero import zotero


EPMC_API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
REQUEST_DELAY = 1.0  # seconds between API calls

ARTICLE_TYPES = {
    "journalArticle",
    "conferencePaper",
    "preprint",
    "report",
    "thesis",
    "bookSection",
    "book",
}


def get_citation_count(
    doi: str | None,
    title: str | None,
    item_type: str = "journalArticle",
) -> int | None:
    """
    Look up citation count on Europe PMC.
    Tries DOI first. Title fallback is only attempted for article-like
    item types, to avoid false matches for datasets and other items.
    Returns None if no match found.
    """
    if doi:
        query = f'DOI:"{doi}"'
    elif title and item_type in ARTICLE_TYPES:
        current_app.logger.warning(
            "No DOI for '%s' (%s), trying title-based lookup",
            title[:60],
            item_type,
        )
        query = f'TITLE:"{title}"'
    else:
        current_app.logger.info(
            "Skipping citation lookup for '%s' (item_type=%s, no DOI)",
            (title or "untitled")[:60],
            item_type,
        )
        return None

    params = {
        "query": query,
        "resultType": "core",
        "format": "json",
        "pageSize": 1,
    }

    try:
        response = requests.get(EPMC_API, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("resultList", {}).get("result", [])
        if results:
            return results[0].get("citedByCount", 0)
        else:
            current_app.logger.warning(
                "No Europe PMC match for query: %s", query
            )
            return None
    except requests.RequestException as e:
        current_app.logger.error("Europe PMC request failed: %s", e)
        return None


@click.command("update-citations")
@with_appcontext
def update_citations_command():
    """Fetch citation counts from Europe PMC and update citation_cache.json."""

    library_id = str(current_app.config.get("ZOTERO_LIBRARY_ID", ""))
    library_type = current_app.config.get("ZOTERO_LIBRARY_TYPE", "group")
    api_key = current_app.config.get("ZOTERO_API_KEY", "")

    if not library_id or not api_key:
        raise click.ClickException(
            "ZOTERO_LIBRARY_ID and ZOTERO_API_KEY must be set in your config."
        )

    cache_file = Path(current_app.root_path).parent / "citation_cache.json"

    current_app.logger.info(
        "Connecting to Zotero library %s (%s)", library_id, library_type
    )
    zot = zotero.Zotero(library_id, library_type, api_key)

    current_app.logger.info("Fetching all items from Zotero...")
    all_items = zot.everything(zot.items())
    items = [
        item for item in all_items
        if item["data"].get("itemType") not in ("attachment", "note")
    ]
    current_app.logger.info("Found %d items", len(items))

    # Load existing cache to preserve any entries not updated this run
    if cache_file.exists():
        with cache_file.open() as f:
            cache = json.load(f)
        current_app.logger.info(
            "Loaded existing cache with %d entries", len(cache)
        )
    else:
        cache = {}

    today = date.today().isoformat()
    updated = 0
    skipped = 0

    for item in items:
        data = item.get("data", {})
        key = item["key"]
        doi = data.get("DOI", "").strip() or None
        title = data.get("title", "").strip() or None
        item_type = data.get("itemType", "unknown")

        current_app.logger.info(
            "Processing [%s] %s", key, (title or "untitled")[:60]
        )

        count = get_citation_count(doi=doi, title=title, item_type=item_type)

        if count is not None:
            cache[key] = {
                "count": count,
                "retrieved": today,
                "doi": doi,
                "title": (title or "")[:80],
                "item_type": item_type,
            }
            updated += 1
        else:
            skipped += 1

        time.sleep(REQUEST_DELAY)

    # Write cache atomically
    tmp_file = cache_file.with_suffix(".tmp")
    with tmp_file.open("w") as f:
        json.dump(cache, f, indent=2)
    tmp_file.replace(cache_file)

    click.echo(
        f"Done. Updated: {updated}, Skipped: {skipped}. "
        f"Cache written to {cache_file}"
    )