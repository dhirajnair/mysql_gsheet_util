**Setup:**

Before you can execute the script,you need to run:

    python3 -m venv ENV
    source ENV/bin/activate
    pip install -r requirements.txt

**Setting up the environment:**

Create a `.env` file with the following variables:
```
Refer .env.example
```

**Google Credentials:**
1. In the Google Cloud console, create a new project or reuse the existing one
2. Via the navigation menu, add new credentials of type OAuth 2.0 (Desktop application)
3. Download the `client_secret....json` and place its contents into `google_credentials.json`


**Running the analysis:**

    python3 main.py

