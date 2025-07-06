"""
Daily Article Generator

This module generates a configurable number of daily news articles for the Mackney Gazette.
It uses the article generation functionality from generate_article.py and configuraton
from articles_daily_config.yaml.

Usage:
    python -m src.generate_articles_daily [--config CONFIG_PATH]

Parameters:
    --config: Optional path to configuration file (defaults to articles_daily_config.yaml in project root)
"""

import os
import yaml
import argparse
import time
import shutil
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
import datetime

# Import the article generation function
from src.utils.data.generate_article import create_new_story


def generate_articles_daily(config_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generate daily articles based on configuration.

    Args:
        config_path: Path to the configuration file. If None, uses default.

    Returns:
        List of generated article data
    """
    # Use default config path if none provided
    if config_path is None:
        # Look for config in project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, "articles_daily_config.yaml")

    # Load configuration
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    # Extract configuration values
    article_count = config["articles"]["count"]
    backup_before_save = config["articles"]["save_options"]["backup_before_save"]
    article_limit = config["articles"]["save_options"]["article_limit"]

    # Display configuration
    print(f"====== DAILY ARTICLE GENERATION - {datetime.datetime.now().strftime('%Y-%m-%d')} ======")
    print(f"Generating {article_count} articles")

    # Backup articles.csv if enabled
    if backup_before_save:
        data_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / 'data'
        articles_csv = data_dir / 'articles.csv'
        
        if articles_csv.exists():
            backup_file = data_dir / f'articles.csv.bak'
            shutil.copy2(articles_csv, backup_file)
            print(f"Backed up articles file to {backup_file}")

    # Generate the specified number of articles
    generated_articles = []
    for i in range(article_count):
        print(f"\n=== Generating article {i+1} of {article_count} ===")
        try:
            # Generate article
            article = create_new_story()
            generated_articles.append(article)
            
            # Add a small delay between articles to avoid rate limiting issues
            if i < article_count - 1:
                time.sleep(1)
                
        except Exception as e:
            print(f"Error generating article {i+1}: {e}")

    print(f"\n=== Article Generation Summary ===")
    print(f"Successfully generated {len(generated_articles)} of {article_count} articles")

    # Prune old articles if limit is set
    if article_limit > 0:
        try:
            data_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / 'data'
            articles_csv = data_dir / 'articles.csv'
            
            if articles_csv.exists():
                # Read existing articles
                articles_df = pd.read_csv(articles_csv)
                
                # Check if we have more than the limit
                if len(articles_df) > article_limit:
                    # Sort by publication date and last_updated (newest first)
                    articles_df['last_updated'] = pd.to_datetime(articles_df['last_updated'])
                    articles_df = articles_df.sort_values(by='last_updated', ascending=False)
                    
                    # Keep only the newest articles up to the limit
                    articles_df = articles_df.head(article_limit)
                    
                    # Save the pruned dataframe
                    articles_df.to_csv(articles_csv, index=False)
                    print(f"Pruned articles.csv to keep the {article_limit} most recent articles")
        except Exception as e:
            print(f"Error pruning old articles: {e}")

    return generated_articles


def main():
    """
    Main function to run the daily article generation.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate daily articles")
    parser.add_argument("--config", help="Path to configuration file", default=None)
    args = parser.parse_args()
    
    # Generate articles
    generate_articles_daily(args.config)


if __name__ == "__main__":
    main()
