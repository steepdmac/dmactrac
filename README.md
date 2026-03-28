# STEEP Data Publication Tracker

A bibliographic web application for tracking and browsing publications related to Project STEEP. Built on [KerkoApp](https://github.com/whiskyechobravo/kerkoapp) — a [Flask](https://flask.palletsprojects.com/) application powered by the [Kerko](https://github.com/whiskyechobravo/kerko) blueprint — with a Zotero group library as the data backend, extended with citation counts from [Europe PMC](https://europepmc.org/).

## Features

- Full-text search and faceted browsing of the STEEP publications library
- Citation counts fetched from Europe PMC and displayed on both search results and individual item pages
- "Has related items" badge surfaced on relevant records
- Atom feed for new publications
- Custom navbar links (Publications, About, Guides) with content pages served directly from Zotero items
- Downloadable records in multiple bibliographic formats
- Responsive Bootstrap layout

## Requirements

- Python 3.10+
- A [Zotero](https://www.zotero.org/) group library with API access
- Internet access to Europe PMC (for citation updates)

## Installation

```bash
git clone <repo-url>
cd <repo-directory>
pip install -e .
```

## Configuration

Copy or edit `config.toml` and set at minimum:

```toml
ZOTERO_LIBRARY_ID = "your_library_id"
ZOTERO_LIBRARY_TYPE = "group"   # or "user"
```

You will also need to provide your Zotero API key. This should be set as an environment variable rather than stored in the config file:

```bash
export KERKOAPP_ZOTERO_API_KEY="your_api_key"
```

Other notable configuration options in `config.toml`:

| Setting | Description |
|---|---|
| `kerko.meta.title` | Site title shown in the browser and navbar |
| `kerko.pages` | Static content pages pulled from Zotero items by key |
| `kerko.facets` | Enable/disable and configure search facets |
| `kerko.features` | Toggle UI features (abstracts, downloads, feeds, etc.) |
| `kerko.zotero.csl_style` | Citation style (default: `apa`) |

See the [Kerko documentation](https://github.com/whiskyechobravo/kerko) for the full list of available settings.

## Running the Application

```bash
flask --app "kerkoapp" run
```

For production, deploy behind a WSGI server such as Gunicorn:

```bash
gunicorn "kerkoapp:create_app()"
```

Before the application can serve content, the Kerko search index must be built:

```bash
flask --app "kerkoapp" kerko sync
```

## Updating Citation Counts

Citation counts are cached in `citation_cache.json` and displayed alongside each bibliographic record. To refresh them from Europe PMC:

```bash
flask --app "kerkoapp" update-citations
```

This command:

1. Fetches all items from the configured Zotero library
2. Queries Europe PMC for each item by DOI (falling back to title for article-like types)
3. Writes updated counts and retrieval dates to `citation_cache.json`

Run this periodically (e.g. weekly via cron) to keep citation counts current.

## Project Structure

```
.
├── __init__.py                  # Application factory
├── cli.py                       # update-citations CLI command
├── config.toml                  # Main configuration file
├── citation_cache.json          # Cached citation counts (auto-generated)
├── pyproject.toml               # Linting configuration (Ruff)
├── templates/
│   └── kerkoapp/
│       ├── layout.html.jinja2           # Base layout (navbar, footer)
│       ├── item.html.jinja2             # Individual item view
│       └── _search-result.html.jinja2  # Search result list item
└── static/
    └── css/
        └── custom.css           # Custom styles (e.g. citation badge)
```

## Customization Notes

### Citation Display

Citation counts are injected into both the search results template (`_search-result.html.jinja2`) and the item detail template (`item.html.jinja2`) via the `citation_cache` template variable. The cache is loaded at application startup and keyed by Zotero item key.

### Badges

A custom `has_related` badge is registered in `__init__.py` using Kerko's `BadgeSpec` API. It appears on any item that has related items linked in Zotero.

### Templates

The templates in this project override Kerko's defaults. When upgrading Kerko, check for upstream changes in the original templates — particularly `kerko/_search-result.html.jinja2`, which is noted as a customized copy.

## Acknowledgements

- [Kerko](https://github.com/whiskyechobravo/kerko) and [KerkoApp](https://github.com/whiskyechobravo/kerkoapp) by Whisky Echo Bravo
- [Zotero](https://www.zotero.org/) for bibliographic data
- [Europe PMC](https://europepmc.org/) for citation data
