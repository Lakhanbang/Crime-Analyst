# Deployment Instructions - Crime Analyst

Follow these steps to deploy your project for free on Render.

## 1. Upload to GitHub
1.  Go to [github.com](https://github.com) and create a new repository (e.g., `crime-analyst`).
2.  Upload the following files from your local folder:
    *   `CrimeInIndia.py`
    *   `States10YearsFinal.csv`
    *   `Dataset 2003-2012.csv`
    *   `states_india (1).geojson`
    *   `requirements.txt`

## 2. Deploy on Render
1.  Create a free account on [render.com](https://render.com).
2.  Click **"New +"** and select **"Web Service"**.
3.  Connect your GitHub account and select your `crime-analyst` repository.
4.  Configure the settings:
    *   **Name**: `crime-analyst-app` (or any name you like)
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn CrimeInIndia:server`
5.  Click **"Deploy Web Service"**.

Once the deployment finishes, Render will provide you with a URL (e.g., `https://crime-analyst-app.onrender.com`) where your app is live!
