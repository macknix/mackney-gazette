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
    
    # Build the complete story chain
    story_chain = []
    current_article = article
    
    # Find the root article (the original story)
    root_article = current_article
    while root_article.get('parent_article_id'):
        parent = next((a for a in articles if a.get('article_id') == root_article.get('parent_article_id')), None)
        if parent:
            root_article = parent
        else:
            break
    
    # Build story chain starting from root
    story_chain = [root_article]
    
    # Add all continuation articles in chronological order
    def find_continuations(parent_id):
        continuations = [a for a in articles if a.get('parent_article_id') == parent_id]
        # Sort by publication date to maintain chronological order
        continuations.sort(key=lambda x: x.get('publication_date', ''))
        return continuations
    
    # Recursively build the chain
    current_level = [root_article]
    while current_level:
        next_level = []
        for article_in_level in current_level:
            continuations = find_continuations(article_in_level.get('article_id'))
            next_level.extend(continuations)
            story_chain.extend(continuations)
        current_level = next_level
    
    # Create story_related list with proper relationships
    story_related = []
    current_index = next((i for i, a in enumerate(story_chain) if a.get('article_id') == article_id), -1)
    
    for i, story_article in enumerate(story_chain):
        if story_article.get('article_id') != article_id:
            if i < current_index:
                relationship = 'Previous story' if i == current_index - 1 else f'Earlier story ({current_index - i} stories back)'
            else:
                relationship = 'Follow-up story' if i == current_index + 1 else f'Later story ({i - current_index} stories ahead)'
            
            story_related.append({
                'article': story_article,
                'relationship': relationship,
                'position': i + 1,
                'total': len(story_chain)
            })
    
    # Get additional related articles from the same category (excluding story chain articles)
    story_chain_ids = set([a.get('article_id') for a in story_chain])
    
    category_related = [a for a in articles 
                       if a.get('category') == article.get('category') 
                       and a.get('article_id') not in story_chain_ids][:3]
    
    # Add story chain position info to the current article
    article['story_position'] = current_index + 1 if current_index >= 0 else 1
    article['story_total'] = len(story_chain)
    
    return render_template(
        'article.html',
        article=article,
        story_related=story_related,
        category_related=category_related,
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
