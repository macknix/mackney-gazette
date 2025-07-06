# Mackney Gazette Website

A news website for the Mackney Gazette, displaying content from generated articles.

## Features

- Responsive design inspired by the Hackney Gazette
- Displays articles from the articles.csv data file
- Category pages for browsing articles by topic
- Article detail pages with images and related content
- Supports story status tracking (ongoing vs concluded)

## Setup & Installation

1. Make sure you have the virtual environment activated:
   ```
   source mackney-gazette-venv/bin/activate
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the website:
   ```
   ./run_website.sh
   ```
   
   Or manually:
   ```
   cd app
   export FLASK_APP=app.py
   export FLASK_ENV=development
   flask run --host=0.0.0.0 --port=5000
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Structure

- `app/app.py` - Main Flask application
- `app/templates/` - HTML templates using Jinja2
- `app/static/` - Static files (CSS, JS, images)
- `data/articles.csv` - Source data for articles

## Adding New Articles

New articles can be added to the website by:

1. Running the article generation script:
   ```
   python src/utils/data/generate_article.py
   ```

2. The new articles will automatically appear on the website.

## Image Search

The website displays images that were searched for based on the article content. These are automatically fetched when new articles are generated.
