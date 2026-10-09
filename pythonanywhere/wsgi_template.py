# WSGI configuration for dmactrac on PythonAnywhere: template, contains NO secrets.
#
# Copy the contents of this file into the web app's WSGI configuration file
# (Web tab -> "WSGI configuration file", e.g.
# /var/www/dmactrac_pythonanywhere_com_wsgi.py) and adjust BASIC SETTINGS.
#
# Secrets (SECRET_KEY, ZOTERO_API_KEY) live in <project_home>/.secrets.toml on
# the server (gitignored; chmod 600). See sample.secrets.toml for the format.

import os
import sys

# --- BASIC SETTINGS ---
username = "dmactrac"        # your PythonAnywhere username
project_name = "dmactrac"    # the folder name of your app
venv_name = "flask-env"      # your virtual environment name

# --- PATHS ---
project_home = f"/home/{username}/{project_name}"
venv_path = f"/home/{username}/.virtualenvs/{venv_name}/bin/activate_this.py"

# Add the project directory to sys.path so `wsgi` and `kerkoapp` can be imported.
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# --- ACTIVATE THE VIRTUAL ENVIRONMENT ---
# Not needed if the Virtualenv field on the Web tab is set; harmless if it is.
if os.path.exists(venv_path):
    with open(venv_path) as file_:
        exec(compile(file_.read(), venv_path, "exec"), dict(__file__=venv_path))

# --- KERKO CONFIGURATION ---
# Absolute paths, because the web app's working directory is not the project.
# Later files override earlier ones; .secrets.toml supplies the secrets.
os.environ["KERKOAPP_CONFIG_FILES"] = (
    f"{project_home}/config.toml;{project_home}/.secrets.toml"
)
os.environ["KERKOAPP_INSTANCE_PATH"] = f"{project_home}/instance"

# --- CREATE THE APP ---
# Import the repo's wsgi.py rather than calling create_app() directly, so the
# "/" -> "/bibliography/" redirect and optional ProxyFix setup are applied.
from wsgi import app as application  # noqa: E402
