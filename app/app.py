"""
Flask application for the Mackney Gazette website.
"""
import os
import json
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)

# Configuration
app.config['ARTICLES_FILE'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'articles.csv')


def load_articles():
    """
    Load and parse articles from the CSV file.
    
    Returns:
        List of article dictionaries
    """
    try:
        df = pd.read_csv(app.config['ARTICLES_FILE'])
        
        # Convert DataFrame to list of dictionaries
        articles = df.to_dict('records')
        
        # Parse the JSON stored in the 'images' column
        for article in articles:
            if 'images' in article and article['images']:
                try:
                    article['images'] = json.loads(article['images'])
                except:
                    article['images'] = []
                    
        # Sort by publication date (newest first)
        articles.sort(key=lambda x: x.get('publication_date', ''), reverse=True)
        
        return articles
    except Exception as e:
        print(f"Error loading articles: {e}")
        return []


def get_categories():
    """
    Get a list of all categories from the articles.
    
    Returns:
        List of category names
    """
    articles = load_articles()
    categories = set()
    
    for article in articles:
        if 'category' in article and article['category']:
            categories.add(article['category'])
            
    return sorted(list(categories))


@app.route('/')
def home():
    """Home page with latest articles."""
    articles = load_articles()
    categories = get_categories()
    
    # Featured articles (first 3)
    featured = articles[:3] if len(articles) >= 3 else articles
    
    # Recent articles (next 6, excluding featured)
    recent = articles[3:9] if len(articles) > 3 else []
    
    return render_template(
        'index.html',
        featured_articles=featured,
        recent_articles=recent,
        categories=categories,
        current_date=datetime.now().strftime('%B %d, %Y')
    )


@app.route('/article/<article_id>')
def article(article_id):
    """Individual article page."""
    articles = load_articles()
    categories = get_categories()
    
    # Find the article with matching ID
    article = next((a for a in articles if a.get('article_id') == article_id), None)
    
    if not article:
        abort(404)
    
    # Get related articles from the same category
    related = [a for a in articles if a.get('category') == article.get('category') and a.get('article_id') != article_id][:3]
    
    return render_template(
        'article.html',
        article=article,
        related_articles=related,
        categories=categories,
        current_date=datetime.now().strftime('%B %d, %Y')
    )


@app.route('/category/<category_name>')
def category(category_name):
    """Category page with articles from a specific category."""
    articles = load_articles()
    categories = get_categories()
    
    # Filter articles by category
    filtered_articles = [a for a in articles if a.get('category') == category_name]
    
    return render_template(
        'category.html',
        category=category_name,
        articles=filtered_articles,
        categories=categories,
        current_date=datetime.now().strftime('%B %d, %Y')
    )


@app.template_filter('format_date')
def format_date(date_str):
    """Format date strings for display."""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%B %d, %Y')
    except:
        return date_str


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
