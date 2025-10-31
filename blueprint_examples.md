I'm creating a Python flask app using the Kerko module. The provided Kerkoapp provides most of the functionality I need, but it's not clear to me how to add new routes to my application because I am unfamiliar with Flask Blueprints. Can you provide an example?

Absolutely — this is a very common question when extending KerkoApp, since it’s built around Flask Blueprints, which are how Flask organizes modular apps.

Let’s go step-by-step through what’s going on and then show an example you can copy into your app.

🧩 Background: What KerkoApp does

KerkoApp wraps Kerko (the Zotero-based bibliography search engine) into a ready-to-run Flask app.
It defines most of its routes (like /search, /item/<id>, etc.) inside a Blueprint called "kerko".

You usually import that into your main app file like this:

```
from flask import Flask
from kerkoapp.app_factory import create_app

app = create_app()
```

That line builds and registers the Kerko blueprint automatically.
To add your own routes, you don’t modify Kerko’s blueprint directly — you just add your own routes to the app.

✅ Example: Adding a new route

Let’s say you want to add a new /about page.

Here’s a minimal example that works with KerkoApp’s structure:

```
# file: wsgi.py (or app.py, depending on your setup)
from flask import Flask, render_template
from kerkoapp.app_factory import create_app

# Create the Kerko-based Flask app
app = create_app()

# Add your own route directly to the app
@app.route("/about")
def about():
    return render_template("about.html")
```
Now you can create templates/about.html and it will render normally.

🧠 Example: Adding your own Blueprint

If you want to keep your extensions modular (the Flask “blueprint” way), you can define your own blueprint:

```
# file: myblueprint.py
from flask import Blueprint, render_template

mybp = Blueprint('mybp', __name__, template_folder='templates')

@mybp.route("/contact")
def contact():
    return render_template("contact.html")
```
Then register it in your main file:

```
# file: wsgi.py
from kerkoapp.app_factory import create_app
from myblueprint import mybp

app = create_app()
app.register_blueprint(mybp)
```
This keeps your custom routes cleanly separated from Kerko’s code.

📁 Typical project structure

Here’s how it might look in your project:
```
my_kerko_app/
├── wsgi.py
├── myblueprint.py
├── templates/
│   ├── about.html
│   ├── contact.html
│   └── ...
└── ...
```
⚙️ Tip: URL prefixes

If you want all your custom routes under a common prefix, use:
```
app.register_blueprint(mybp, url_prefix="/extra")
```

Then /contact becomes /extra/contact.

Would you like me to show an example where your custom route interacts with Kerko’s search results (e.g., listing the latest items or a custom filtered view)? That’s a bit more advanced, but very doable once you’re comfortable with Blueprints.

Yes

Perfect 👍 — let’s walk through how to add a custom route that interacts with Kerko’s search results using Flask and Kerko’s internal API.
🎯 Goal

You’ll add a new route, /latest, that shows the most recently added Zotero items from your Kerko index.

This uses Kerko’s internal searcher and document model, so it behaves like the main app but under your own control.

🧱 Step-by-step example
1. Create a new file — myblueprint.py
```
# myblueprint.py
from flask import Blueprint, render_template, current_app
from kerko.search import get_searcher
from whoosh.sorting import FieldFacet

mybp = Blueprint('mybp', __name__, template_folder='templates')

@mybp.route("/latest")
def latest_items():
    """Show the most recently added bibliography items."""
    searcher = get_searcher(current_app)

    # Sort by 'year' descending (assuming Kerko indexed that field)
    facet = FieldFacet("year", reverse=True)

    results = searcher.search("", sortedby=facet, limit=10)

    items = []
    for hit in results:
        item = {
            "title": hit.get("title", "(Untitled)"),
            "year": hit.get("year"),
            "authors": hit.get("authors"),
            "url": f"/item/{hit['key']}",
        }
        items.append(item)

    return render_template("latest.html", items=items)
```
2. Register the blueprint in your main app file
```
# wsgi.py
from kerkoapp.app_factory import create_app
from myblueprint import mybp

app = create_app()
app.register_blueprint(mybp)
```
3. Create the template — templates/latest.html
```
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Latest Items</title>
  </head>
  <body>
    <h1>Latest Bibliography Items</h1>
    <ul>
      {% for item in items %}
        <li>
          <a href="{{ item.url }}">{{ item.title }}</a>
          {% if item.authors %} — {{ item.authors }}{% endif %}
          {% if item.year %} ({{ item.year }}){% endif %}
        </li>
      {% else %}
        <li>No items found.</li>
      {% endfor %}
    </ul>
  </body>
</html>
```
🧠 How it works

get_searcher(current_app) gives you Kerko’s Whoosh searcher instance.

searcher.search() runs a query ("" means “everything”).

sortedby=FieldFacet("year", reverse=True) sorts newest first.

Each hit in results corresponds to a Zotero item from your index.

You link to /item/<key> — which Kerko already serves.

⚙️ Optional: Filter by tag or collection

You can modify the search query easily. For example:
```
results = searcher.search("tag:climate", sortedby=facet, limit=10)
```
or
```
results = searcher.search("collection:reports", sortedby=facet, limit=10)
```
🔧 Common pitfall

If you try to use searcher before the Kerko index is built, you’ll get an error like:
```
RuntimeError: No index found at path
```

Make sure you’ve run:
```
flask kerko build
```

at least once.

Would you like me to show how to use Kerko’s SearchForm (the same one used on the main search page) in a custom route, so you can have a specialized search view (e.g., “Search only reports”)?

🧩 Extending KerkoApp: Adding a Custom Filtered Search Route

This guide shows how to create a custom Flask route that reuses Kerko’s search functionality but filters results automatically — for example, to display only items tagged as "report".

🎯 Goal

Add a /reports route that:

Uses Kerko’s existing search form and rendering.

Automatically filters results to items tagged "report".

Preserves pagination, sorting, and styling from Kerko.

🧱 Step 1 — Create or extend your Blueprint

Create a file called myblueprint.py:

# myblueprint.py
from flask import Blueprint, render_template, current_app, request
from kerko.search import Searcher
from kerko.forms import SearchForm
from kerko.views import render_search_results

mybp = Blueprint('mybp', __name__, template_folder='templates')


@mybp.route("/reports")
def reports():
    """Show search results limited to 'report' items."""
    app = current_app
    config = app.config["KERKO_COMPOSER"]

    # Initialize the Kerko searcher and form
    searcher = Searcher(config)
    form = SearchForm(request.args, config=config)

    # Apply the 'report' tag filter automatically
    query = form.q.data or ""
    query = f"{query} tag:report"

    results = searcher.search(query, page=form.page.data or 1)

    # Reuse Kerko’s built-in search rendering
    return render_search_results(form, results, config)

🧱 Step 2 — Register the Blueprint

In your main app file (usually wsgi.py):

# wsgi.py
from kerkoapp.app_factory import create_app
from myblueprint import mybp

app = create_app()
app.register_blueprint(mybp)

🧱 Step 3 — (Optional) Create a Custom Template

If you’d like a custom title or description above the results, create templates/reports.html:

{% extends "kerko/search.html" %}
{% block content %}
  <h1>Reports</h1>
  <p>These are all items tagged as reports.</p>
  {{ super() }}
{% endblock %}


Then, in your route, replace the last line with:

return render_template("reports.html", form=form, results=results, config=config)

🧱 Step 4 — Visit Your New Route

Start your Flask app and open:

http://localhost:5000/reports


You’ll see a normal Kerko search interface showing only items tagged "report".

🧠 How It Works
Component	Purpose
Searcher	Kerko’s interface to the Whoosh index (handles ranking, filtering, etc.)
SearchForm	Parses query parameters (q, sort, page, etc.)
render_search_results	Renders results with Kerko’s built-in Jinja templates
tag:report filter	Ensures only report-tagged items are included
⚙️ Variations

You can easily modify the query to filter by collection, multiple tags, or date:

# Filter by a specific collection
query = f"{query} collection:reports"

# Filter by multiple tags
query = f"{query} (tag:report OR tag:policy)"

# Filter by tag and year
query = f"{query} tag:report AND year:2023"

🧩 Optional Enhancement — Add a Search Box

To let users refine searches within this subset, include the search form field in your reports.html template:

<form method="get" action="{{ url_for('mybp.reports') }}">
  {{ form.q(size=40, placeholder="Search within reports...") }}
  <button type="submit">Search</button>
</form>

{{ super() }}


This way, users can perform keyword searches but still remain filtered to "tag:report" items.